from typing import Optional
from pydantic import BaseModel

class ReceiptBase(BaseModel):
    id_penanganan: str
    receipt_number: str
    transaction_type: str
    summary_type: str
    remark: Optional[str] = None


class ReceiptCreateRequest(ReceiptBase):
    fc_id: int
    created_by: str
    customer_address: Optional[str] = None
