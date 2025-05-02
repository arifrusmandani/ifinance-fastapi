import datetime
import json

from app.src.router.download.crud import CRUDDownload
from app.src.router.download.schema import EnumDownloadEntity
from app.src.utils.file_generator import FileGenerator


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
