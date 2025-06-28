from typing import Literal

from pydantic import BaseModel


class BaseResponse(BaseModel):
    status: Literal["success", "error"]