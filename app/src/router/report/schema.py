from typing import List, Optional
from pydantic import BaseModel
from app.src.router.response import BaseListResponse, BaseResponse
from app.src.database.models.transaction import TransactionType


class CategoryReport(BaseModel):
    category: str
    type: TransactionType
    amount: float


class CategoryReportResponse(BaseResponse):
    data: Optional[CategoryReport] = None


class CategoryReportListResponse(BaseListResponse):
    data: List[CategoryReport] = []


class MonthlyChartData(BaseModel):
    name: str  # Month abbreviation (Jan, Feb, etc.)
    income: float
    expense: float


class MonthlyChartResponse(BaseResponse):
    data: List[MonthlyChartData] = []
