from typing import Literal, List

from backend.model.response.base_response import BaseResponse


class UploadResponse(BaseResponse):
    status: Literal["success"] = "success"
    message: str
    filename: str
    shape: tuple[int, int]
    columns: List[str]