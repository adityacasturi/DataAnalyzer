from typing import Literal

from backend.model.output.tool_output import ToolOutput

class PlotOutput(ToolOutput):
    type: Literal["plot"] = "plot"
    data: str
    caption: str