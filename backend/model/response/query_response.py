from typing import Literal, Optional

from backend.model.response.base_response import BaseResponse

class QueryResponse(BaseResponse):
    status: Literal["success"] = "success"
    final_answer: str
    generated_plot: Optional[str] = None