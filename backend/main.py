import io
import os
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, status
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.model.response.query_response import QueryResponse
from backend.model.user_query import UserQuery
from backend.model.response.upload_response import UploadResponse
from backend.tool.python_tool import PythonTool


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")

    app.state.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    app.state.agent_executor = None

    yield

app = FastAPI(lifespan=lifespan)


def create_agent_executor(df: pd.DataFrame, llm: ChatGoogleGenerativeAI) -> AgentExecutor:
    tools = [PythonTool(df=df)]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="output")

    prompt = hub.pull("hwchase17/react-chat")
    prompt.template = f"""You are an expert data analyst equipped with a powerful python interpreter.

        TOOL GUIDANCE:
        1. Your ONLY tool is the `python_interpreter`.
        2. The tool will return a dictionary. Check the 'type' key to understand the output.
        3. The user's DataFrame, `df`, is already loaded.
           - Shape: {df.shape}
           - Columns: {list(df.columns)}
           - DO NOT try to load the data yourself.
        
        Begin!
        """ + prompt.template

    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        request.app.state.agent_executor = create_agent_executor(df, request.app.state.llm)

        return UploadResponse(
            message="File uploaded and agent created successfully.",
            filename=file.filename,
            shape=df.shape,
            columns=list(df.columns)
        )
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during file processing: {e}")


@app.post("/invoke", response_model=QueryResponse)
async def invoke_agent(request: Request, user_query: UserQuery):
    agent_executor = request.app.state.agent_executor

    if not isinstance(agent_executor, AgentExecutor):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No dataset loaded. Please upload a CSV file via the /upload endpoint first."
        )

    try:
        response = await agent_executor.ainvoke({"input": user_query.input})

        final_answer = response.get("output", "No text output was generated.")
        image_output = None

        if "intermediate_steps" in response and response["intermediate_steps"]:
            for action, observation in reversed(response["intermediate_steps"]):
                if action.tool == "python_interpreter" and isinstance(observation, dict):
                    if observation.get("type") == "plot":
                        image_output = observation.get("data")
                        break

        return QueryResponse(final_answer=final_answer, generated_plot=image_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent failed to process the request: {e}")