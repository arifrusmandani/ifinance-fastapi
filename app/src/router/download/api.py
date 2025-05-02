import datetime
from fastapi import Depends, Form, Response, status, Security
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.src.exception.handler.context import api_exception_handler
from app.src.router.download.object import DownloadObject
from app.src.router.download.schema import EnumDownloadEntity
from app.src.router.security import verify_token, check_permission

router = InferringRouter()


@cbv(router)
class DownloadView:
    """Download View Router"""
    res: Response
    download_object = DownloadObject()

    @router.get("/{data_type}/{fc_id}/csv")
    async def get_csv_data(
        self,
        data_type: EnumDownloadEntity,
        fc_id: int,
        _: dict = Depends(verify_token),
    ):
        date_now = datetime.datetime.now().strftime("%Y-%m-%d")
        file_name = f"{data_type.value}_{fc_id}_{date_now}.csv"

        data = await self.download_object.download_data_to_csv(fc_id, data_type)
        response = StreamingResponse(
            iter([data.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
        return response
