from typing import Literal

from backend.model.output.tool_output import ToolOutput


class TextOutput(ToolOutput):
    type: Literal["text"] = "text"
    data: str