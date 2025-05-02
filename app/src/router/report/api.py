import datetime
from fastapi import Response, status
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi import APIRouter, Security

from app.src.exception.handler.context import api_exception_handler
from app.src.router.security import check_permission
from app.src.router.report.object import ReportObject
from app.src.core.config import PAGINATION_LIMIT
from app.src.router.report.schema import (
    AssignmentSummaryList, FollowUpStatus, PaymentStatus, VisitResultReportList)


router = APIRouter()


page = 'report'


@cbv(router)
class ReportView:
    """ Contract View Router"""
    res: Response
    report_object = ReportObject()

    @router.get("/assignment-summary", response_model=AssignmentSummaryList)
    async def get_assignment_summary(
            self,
            fc_name: str = None,
            fc_type_id: int = None,
            offset: int = 0,
            limit: int = PAGINATION_LIMIT,
            authorized_user: dict = Security(check_permission, scopes=[f"{page}.get"])) -> dict:
        """
        Get tracking overview
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            data, record_count = await self.report_object.get_assignment_summary(
                authorized_user=authorized_user,
                fc_name=fc_name,
                fc_type_id=fc_type_id,
                offset=offset,
                limit=limit
            )
            response_builder.status = True
            response_builder.code = status.HTTP_200_OK
            response_builder.message = "Success get assignment summary data!"
            response_builder.data = jsonable_encoder(data)
            response_builder.record_count = record_count

        return response_builder.to_dict()

    @router.get("/visit-result", response_model=VisitResultReportList)
    async def get_visit_result_report(
            self,
            keyword: str = None,
            fc_id: int = None,
            bucket: str = None,
            payment_status: PaymentStatus = None,
            followup_status: FollowUpStatus = None,
            start_date: datetime.date = None,
            end_date: datetime.date = None,
            offset: int = 0,
            limit: int = PAGINATION_LIMIT,
            authorized_user: dict = Security(check_permission, scopes=[f"{page}.get_visit_result"])
    ) -> dict:
        """
        Get visit result report
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            data, record_count = await self.report_object.get_visit_result_report(
                authorized_user=authorized_user,
                keyword=keyword,
                fc_id=fc_id,
                bucket=bucket,
                payment_status=payment_status,
                followup_status=followup_status,
                start_date=start_date,
                end_date=end_date,
                offset=offset,
                limit=limit
            )
            response_builder.status = True
            response_builder.code = status.HTTP_200_OK
            response_builder.message = "Success get visit result report!"
            response_builder.data = jsonable_encoder(data)
            response_builder.record_count = record_count

        return response_builder.to_dict()
