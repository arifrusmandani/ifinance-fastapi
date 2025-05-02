from app.src.router.receipt.crud import CRUDReceipt
from app.src.router.receipt.schema import ReceiptCreateRequest


class ReceiptObject:
    """ Receipt Object """

    def __init__(self, authorized_user):
        self.crud_receipt = CRUDReceipt()
        self.authorized_user = authorized_user

    async def create_payment_receipt(self, data: ReceiptCreateRequest):
        visit_result = await self.crud_receipt.get_followup_result_data(data.id_penanganan)
        if visit_result:
            data.customer_address = visit_result.customer_address

        data = await self.crud_receipt.create_data(data)
        return data
