from pydantic import BaseModel


class ToolOutput(BaseModel):
    type: str