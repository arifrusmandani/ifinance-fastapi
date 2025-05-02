from fastapi import Security, Response, status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.src.exception.handler.context import api_exception_handler
from app.src.router.receipt.object import ReceiptObject
from app.src.router.receipt.schema import ReceiptBase, ReceiptCreateRequest


router = InferringRouter()


@cbv(router)
class ReceiptView:
    """ Receipt View Router"""
    res: Response
    receipt_object = ReceiptObject

    @router.post("/")
    async def create_payment_receipt_log(
        self,
        request: ReceiptBase
    ) -> dict:
        """
        Create payment receipt log
        """
        with api_exception_handler(self.res) as response_builder:
            receipt_schema = ReceiptCreateRequest(
                **request.dict()
            )
            data = await self.receipt_object.create_payment_receipt(receipt_schema)
            response_builder.status = True
            response_builder.code = http_status.HTTP_201_CREATED
            response_builder.message = "success"
            response_builder.data = jsonable_encoder(data)
        return response_builder.to_dict()
