from typing import List, Optional
from pydantic import BaseModel
from app.src.router.response import BaseListResponse, BaseResponse
from app.src.database.models.transaction import TransactionType
from datetime import date, datetime


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


class DashboardSummaryItem(BaseModel):
    label: str
    value: float
    percent: float
    last_month: float


class DashboardSummaryResponse(BaseResponse):
    data: List[DashboardSummaryItem] = []


class MostExpenseCategory(BaseModel):
    category_code: str
    category_name: str
    amount: float
    color: str
    percentage: float


class MostExpenseCategoryResponse(BaseResponse):
    data: List[MostExpenseCategory] = []


class CategoryAmount(BaseModel):
    category_code: str
    category_name: str
    amount: float
    color: str


class CategoryAmountResponse(BaseResponse):
    data: List[CategoryAmount] = []


class CashflowTransaction(BaseModel):
    category_code: Optional[str] = None
    description: Optional[str] = None
    amount: float
    date: datetime


class MonthCashflow(BaseModel):
    month: str  # YYYY-MM format
    income: List[CashflowTransaction] = []
    expense: List[CashflowTransaction] = []


class CashflowDataResponse(BaseResponse):
    data: List[MonthCashflow] = []
