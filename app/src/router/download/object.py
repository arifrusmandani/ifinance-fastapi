import datetime
import json

from app.src.router.download.crud import CRUDDownload
from app.src.router.download.schema import EnumDownloadEntity
from app.src.utils.file_generator import FileGenerator
from app.src.router.report.schema import PaymentStatus, FollowUpStatus, VisitResultReport
from app.src.router.report.object import ReportObject


class DownloadObject:
    """Download Object"""
    crud_download = CRUDDownload()

    async def download_data_to_csv(self, fc_id: int, data_type: EnumDownloadEntity):
        """Download data to csv"""
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year

        if data_type == EnumDownloadEntity.assignments:
            headers, rows = await self.crud_download.get_assignment_data(fc_id)
        elif data_type == EnumDownloadEntity.agreements:
            headers, rows = await self.crud_download.get_agreement_data(fc_id)
        elif data_type == EnumDownloadEntity.customers:
            headers, rows = await self.crud_download.get_customer_data(fc_id)
        elif data_type == EnumDownloadEntity.assets:
            headers, rows = await self.crud_download.get_agreement_asset_data(fc_id)
        elif data_type == EnumDownloadEntity.followup_results:
            headers, rows = await self.crud_download.get_followup_result_data(fc_id, current_month, current_year)
        elif data_type == EnumDownloadEntity.customer_history:
            headers, rows = await self.crud_download.get_customer_history_data(fc_id)
        elif data_type == EnumDownloadEntity.ptp_followup_results:
            headers, rows = await self.crud_download.get_ptp_followup_result_data(fc_id)
        else:
            raise ValueError("Invalid data type")

        csv_data = await FileGenerator().generate_csv(headers=headers, rows=rows)

        return csv_data

    async def download_visit_result_data_to_csv(
        self,
        authorized_user: dict,
        keyword: str = None,
        fc_id: int = None,
        bucket: str = None,
        payment_status: PaymentStatus = None,
        followup_status: FollowUpStatus = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ):
        data, _ = await ReportObject.get_visit_result_report(
            self,
            authorized_user=authorized_user,
            keyword=keyword,
            fc_id=fc_id,
            bucket=bucket,
            payment_status=payment_status,
            followup_status=followup_status,
            start_date=start_date,
            end_date=end_date,
        )
        headers = VisitResultReport.model_json_schema().get('properties', {}).keys()
        rows = [list(json.loads(item.json()).values()) for item in data]
        csv_data = await FileGenerator().generate_csv(
            headers=list(headers), rows=rows)
        result = csv_data
        return result