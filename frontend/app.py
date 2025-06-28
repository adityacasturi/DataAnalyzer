import base64
import json

import requests
import streamlit as st

st.set_page_config(page_title="Data Analysis Agent", layout="wide")

BACKEND_URL = "http://localhost:8000"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "awaiting_response" not in st.session_state:
    st.session_state.awaiting_response = False


def process_file(file_uploader_object):
    st.session_state.messages = []
    try:
        files = {"file": (file_uploader_object.name, file_uploader_object.getvalue(), "text/csv")}
        response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=30)

        response_data = response.json()

        if response.status_code == 200 and response_data.get("status") == "success":
            st.success(response_data.get("message", "File uploaded successfully!"))
            return True
        else:
            detail = response_data.get("detail", "No details provided.")
            st.error(f"Upload failed: {detail}")
            return False

    except requests.exceptions.RequestException:
        st.error(f"Connection error: Could not connect to the backend at {BACKEND_URL}.")
        return False
    except json.JSONDecodeError:
        st.error("Failed to decode server response. The backend might be down or returning invalid data.")
        return False


def send_user_query(message: str) -> dict:
    try:
        payload = {"input": message}
        response = requests.post(
            f"{BACKEND_URL}/invoke",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        return response.json()

    except requests.exceptions.RequestException:
        return {
            "status": "error",
            "message": "Connection Error",
            "detail": f"Could not connect to the backend at {BACKEND_URL}."
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Invalid Response",
            "detail": "Failed to decode server response. The backend might have crashed."
        }

## UI ##

with st.sidebar:
    st.title("Setup")

    if not st.session_state.file_uploaded:
        uploaded_file = st.file_uploader("Upload your CSV file:", type=['csv'])

        if uploaded_file:
            with st.spinner("Processing file..."):
                if process_file(uploaded_file):
                    st.session_state.file_uploaded = True
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.rerun()
    else:
        st.write(f"**File:** `{st.session_state.uploaded_filename}`")
        if st.button("Upload New File"):
            st.session_state.file_uploaded = False
            st.session_state.messages = []
            if "uploaded_filename" in st.session_state:
                del st.session_state.uploaded_filename
            st.rerun()

    st.write("---")
    ready_status = "🟢 Ready to Chat" if st.session_state.file_uploaded else "⚪ Awaiting CSV File"
    st.write(f"**Status:** {ready_status}")

st.title("Chat with your CSV")
st.write("This agent can answer questions, perform analysis, and generate plots from your data.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("generated_plot"):
            try:
                image_bytes = base64.b64decode(message["generated_plot"])
                st.image(image_bytes, caption="Generated Plot", use_container_width='auto')
            except Exception as e:
                st.error(f"Could not display image: {e}")

if st.session_state.awaiting_response:
    last_user_message = next((msg["content"] for msg in reversed(st.session_state.messages) if msg["role"] == "user"),
                             None)

    if last_user_message:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = send_user_query(last_user_message)

                if response_data.get("status") == "success":
                    assistant_message = {
                        "role": "assistant",
                        "content": response_data.get("final_answer", "Sorry, I didn't get a valid response."),
                        "generated_plot": response_data.get("generated_plot")
                    }
                else:
                    assistant_message = {
                        "role": "assistant",
                        "content": "Sorry, I encountered an error. Please check the backend logs for details or try rephrasing your question.",
                    }

                st.session_state.messages.append(assistant_message)
                st.session_state.awaiting_response = False
                st.rerun()

if st.session_state.file_uploaded:
    if prompt := st.chat_input("Ask a question about your data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.awaiting_response = True
        st.rerun()
else:
    st.chat_input("Please upload a CSV file to begin.", disabled=True)
