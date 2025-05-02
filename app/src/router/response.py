from pydantic import BaseModel
from typing import Any, List, Optional


class BaseResponse(BaseModel):
    status: bool
    code: int
    message: str
    data: Any


class BaseListResponse(BaseModel):
    status: bool
    code: int
    message: str
    data: Any
    record_count: int = 0
