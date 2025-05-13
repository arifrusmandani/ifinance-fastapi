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
    MonthlyChartResponse
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
