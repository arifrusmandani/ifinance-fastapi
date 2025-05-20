from fastapi import APIRouter, Depends, Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status as http_status
from fastapi.encoders import jsonable_encoder
from datetime import date, datetime
from typing import Optional

from app.src.database.models.user import User
from app.src.router.report.object import ReportObject
from app.src.router.report.schema import (
    CategoryReportListResponse,
    MonthlyChartResponse,
    DashboardSummaryResponse,
    MostExpenseCategoryResponse,
    CategoryAmountResponse,
    CashflowDataResponse
)
from app.src.router.user.security import get_authorized_user
from app.src.exception.handler.context import api_exception_handler

router = InferringRouter()


@cbv(router)
class ReportView:
    """ Report View Router """
    res: Response

    def __init__(self, authorized_user: User = Depends(get_authorized_user)):
        self.authorized_user = authorized_user
        self.report_object = ReportObject(authorized_user)

    @router.get("/category", response_model=CategoryReportListResponse)
    async def get_category_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get category-wise transaction report for the current user.

        - **start_date**: Filter transactions from this date (optional)
        - **end_date**: Filter transactions until this date (optional)

        Returns a list of category reports with income, expense, and balance.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            reports = await self.report_object.get_category_report(
                user_id=self.authorized_user.id,
                start_date=start_date,
                end_date=end_date
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Category report retrieved successfully"
            response_builder.data = jsonable_encoder(reports)
            return response_builder.to_dict()

    @router.get("/monthly", response_model=MonthlyChartResponse)
    async def get_monthly_chart(
        self,
        year: int = datetime.now().year
    ) -> dict:
        """
        Get monthly income vs expense data for the current user.

        - **year**: Year to get data for (defaults to current year)

        Returns monthly data with income and expense totals.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            reports = await self.report_object.get_monthly_chart_data(
                user_id=self.authorized_user.id,
                year=year
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Monthly chart data retrieved successfully"
            response_builder.data = jsonable_encoder(reports)
            return response_builder.to_dict()

    @router.get("/dashboard-summary", response_model=DashboardSummaryResponse)
    async def get_dashboard_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get dashboard summary data for the current user.

        - **start_date**: Filter transactions from this date (optional, default: current month)
        - **end_date**: Filter transactions until this date (optional, default: current month)

        Returns total balance, total period expenses, total period income, percent change, and last month value for each metric.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            summary = await self.report_object.get_dashboard_summary(
                user_id=self.authorized_user.id,
                start_date=start_date,
                end_date=end_date
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Dashboard summary data retrieved successfully"
            response_builder.data = jsonable_encoder(summary)
            return response_builder.to_dict()

    @router.get("/most-expense-category", response_model=MostExpenseCategoryResponse)
    async def get_most_expense_by_category(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get most expensive categories for the current user.

        - **start_date**: Filter transactions from this date (optional, default: current month)
        - **end_date**: Filter transactions until this date (optional, default: current month)

        Returns a list of categories with their total expense amount and percentage of total expenses.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            categories = await self.report_object.get_most_expense_by_category(
                user_id=self.authorized_user.id,
                start_date=start_date,
                end_date=end_date
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Most expense by category retrieved successfully"
            response_builder.data = jsonable_encoder(categories)
            return response_builder.to_dict()

    @router.get("/income-categories", response_model=CategoryAmountResponse)
    async def get_income_categories(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get income categories with their amounts for the current user.

        - **start_date**: Filter transactions from this date (optional, default: current month)
        - **end_date**: Filter transactions until this date (optional, default: current month)

        Returns a list of income categories with their amounts and total income.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            categories = await self.report_object.get_income_categories(
                user_id=self.authorized_user.id,
                start_date=start_date,
                end_date=end_date
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Income categories retrieved successfully"
            response_builder.data = jsonable_encoder(categories)
            return response_builder.to_dict()

    @router.get("/expense-categories", response_model=CategoryAmountResponse)
    async def get_expense_categories(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get expense categories with their amounts for the current user.

        - **start_date**: Filter transactions from this date (optional, default: current month)
        - **end_date**: Filter transactions until this date (optional, default: current month)

        Returns a list of expense categories with their amounts and total expense.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            categories = await self.report_object.get_expense_categories(
                user_id=self.authorized_user.id,
                start_date=start_date,
                end_date=end_date
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Expense categories retrieved successfully"
            response_builder.data = jsonable_encoder(categories)
            return response_builder.to_dict()

    @router.get("/cashflow-data", response_model=CashflowDataResponse)
    async def get_cashflow_data(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get cashflow data grouped by month for the current user.

        - **start_date**: Filter transactions from this date (optional, default: current year start)
        - **end_date**: Filter transactions until this date (optional, default: current year end)

        Returns a list of monthly cashflow data, including income and expense transactions.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            cashflow_data = await self.report_object.get_cashflow_data(
                user_id=self.authorized_user.id,
                start_date=start_date,
                end_date=end_date
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Cashflow data retrieved successfully"
            response_builder.data = jsonable_encoder(cashflow_data)
            return response_builder.to_dict()
