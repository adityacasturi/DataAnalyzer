from typing import Literal

from backend.model.output.tool_output import ToolOutput

class ErrorOutput(ToolOutput):
    type: Literal["error"] = "error"
    message: str