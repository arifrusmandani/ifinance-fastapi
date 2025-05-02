from fastapi import Response, status as http_status, Security
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.src.exception.handler.context import api_exception_handler
from app.src.router.customer.object import CustomerObject
from app.src.router.customer.schema import CustomerHistoryBaseSchema, CustomerHistoryCreateSchema, CustomerHistoryDetailResponse, CustomerHistoryListResponse
from app.src.router.security import check_permission


router = InferringRouter()


@cbv(router)
class CustomerView:
    """ Customer View Router"""
    res: Response

    def __init__(self, authorized_user: str = Security(check_permission, scopes=["fc.default"])):
        self.authorized_user = authorized_user
        self.customer_object = CustomerObject(authorized_user)

    @router.post("/history/{followup_session_id}", response_model=CustomerHistoryDetailResponse)
    async def create_customer_update(
        self,
        followup_session_id: int,
        data: CustomerHistoryBaseSchema
    ) -> dict:
        """
        Create Customer History
        """
        with api_exception_handler(self.res) as response_builder:
            create_data = CustomerHistoryCreateSchema(
                **data.dict(),
                fc_id=self.authorized_user["id"],
                updated_by=self.authorized_user["fullname"],
                followup_session_id=followup_session_id
            )
            data = await self.customer_object.create_customer_update(create_data)
            response_builder.status = True
            response_builder.code = http_status.HTTP_201_CREATED
            response_builder.message = "success"
            response_builder.data = jsonable_encoder(data)
        return response_builder.to_dict()

    @router.get("/{customer_no}/history", response_model=CustomerHistoryListResponse)
    async def get_customer_history(
        self,
        customer_no: str,
        is_canceled: bool = False
    ) -> dict:
        """
        Get Customer History
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            data, count = await self.customer_object.get_customer_update_history(
                customer_no=customer_no, is_canceled=is_canceled
            )
            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "success"
            response_builder.data = jsonable_encoder(data)
            response_builder.record_count = count
        return response_builder.to_dict()

    @router.get("/{customer_no}/history/{history_id}", response_model=CustomerHistoryDetailResponse)
    async def get_customer_history_detail(
        self,
        customer_no: str,
        history_id: str,
    ) -> dict:
        """
        Get Customer History
        """
        with api_exception_handler(self.res) as response_builder:
            data = await self.customer_object.get_customer_history_detail(
                customer_no=customer_no, history_id=history_id
            )
            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "success"
            response_builder.data = jsonable_encoder(data)
        return response_builder.to_dict()
