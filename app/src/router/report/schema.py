from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from app.src.router.response import BaseListResponse


class FollowUpStatus(Enum):
    VISIT = "VISIT"
    CALL = "CALL"


class PaymentStatus(Enum):
    PAID = "PAID"
    PTP = "PTP"
    PARTIAL = "PARTIAL"
    UNPAID = "UNPAID"


class AssignmentSummary(BaseModel):
    fc_nip: str | None
    fc_name: str | None
    fc_type_id: int | None
    fc_areas: str | None
    number_of_customers: int | None
    total_distance: float | None
    score_gap_percent: int | None


class AssignmentSummaryList(BaseListResponse):
    data: list[AssignmentSummary] = []


class VisitResultReport(BaseModel):
    customer_name: str 
    customer_number: str
    agreement_number: str
    fc_name: str
    fc_id: int
    os_ni: int
    overdue_amount: int
    paid_amount: int | None = None
    bucket: str
    payment_status: PaymentStatus
    followup_status: FollowUpStatus
    visit_date: datetime | None = None
    assigned_date: datetime | None = None
    attachment: list | None = []


class VisitResultReportList(BaseListResponse):
    data: list[VisitResultReport] = []
