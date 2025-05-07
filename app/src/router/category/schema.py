from typing import List, Optional
from pydantic import BaseModel
from app.src.database.models.transaction import TransactionType
from app.src.router.response import BaseListResponse, BaseResponse


class CategoryBase(BaseModel):
    name: str
    code: str
    type: TransactionType
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(BaseResponse):
    data: CategoryBase


class CategoryListResponse(BaseListResponse):
    data: List[CategoryBase]
