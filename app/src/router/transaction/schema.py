from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.src.database.models.transaction import TransactionType
from app.src.router.response import BaseListResponse, BaseResponse


class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    type: TransactionType
    category_code: Optional[str] = None
    date: datetime = datetime.now()


class TransactionCreate(TransactionBase):
    user_id: int


class TransactionDetail(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime = None

class TransactionDetailList(TransactionBase):
    id: int
    user_id: int
    category_name: str
    category_icon: str
    created_at: datetime

class TransactionResponse(BaseResponse):
    data: Optional[TransactionDetail] = None


class TransactionListResponse(BaseListResponse):
    data: List[TransactionDetailList] = []
