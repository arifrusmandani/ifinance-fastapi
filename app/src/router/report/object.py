import datetime

from app.src.router.report.crud import CRUDReport
from app.src.router.report.schema import (
    AssignmentSummary, PaymentStatus, FollowUpStatus, VisitResultReport)
from app.src.database.models.agreement_overdue import AgreementOverdue

class ReportObject:
    pass