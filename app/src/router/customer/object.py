import uuid
from app.src.base.crud import CRUDBase
from app.src.core.config import GCS_BUCKET_IMAGE_CUSTOMER
from app.src.router.customer.crud import CRUDCustomerHistory
from app.src.router.customer.schema import CustomerHistoryCreateSchema


class CustomerObject:
    """ Customer Object """

    def __init__(self, authorized_user):
        self.crud_history = CRUDCustomerHistory()
        self.authorized_user = authorized_user

    async def get_customer_update_history(self, customer_no: str, is_canceled: bool) -> tuple:
        """
        Get customer update history.
        """
        res, count = await self.crud_history.get_customer_update_history(customer_no, is_canceled)
        return res, count
