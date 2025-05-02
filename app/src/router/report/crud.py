import datetime
from sqlalchemy import func, case, and_, or_
from sqlalchemy.orm import aliased
from app.src.database.session import session_manager
from app.src.database.models.agreement_overdue import AgreementOverdue
from app.src.router.report.schema import PaymentStatus, FollowUpStatus


class CRUDReport:
    pass