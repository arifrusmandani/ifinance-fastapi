import enum
from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, String, Integer, Date, Boolean, Enum
from app.src.database.engine import BaseModel


class AgreementStatus(enum.Enum):
    OVD = "OVD"
    WO = "WO"


class CISStatus(enum.Enum):
    WAITING_FOR_ASSIGNMENT = "WAITING_FOR_ASSIGNMENT"
    AUTO_ASSIGNMENT_SUCCESS = "AUTO_ASSIGNMENT_SUCCESS"
    AUTO_ASSIGNMENT_FAILED = "AUTO_ASSIGNMENT_FAILED"
    MANUAL_ASSIGNMENT = "MANUAL_ASSIGNMENT"


class AgreementOverdue(BaseModel):
    __tablename__ = "agreement_overdue"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    agreement_number = Column(String(32), nullable=False)
    agreement_id = Column(String(16), nullable=True)
    customer_no = Column(String(32), nullable=False)
    customer_name = Column(String(64), nullable=False)
    bucket = Column(String(16), nullable=False)
    overdue_amount = Column(BigInteger, nullable=False)
    overdue_days = Column(Integer, nullable=False)
    os_ni = Column(BigInteger, nullable=False)
    os_interest = Column(BigInteger, nullable=False)
    due_date = Column(Date, nullable=False)
    branch_id = Column(Integer, nullable=True)
    branch_code = Column(String(16), nullable=False)
    branch = Column(String(32), nullable=True)
    visit_request = Column(Boolean, nullable=True)
    cis_status = Column(
        Enum(CISStatus, name="cis_status"),
        nullable=False,
        default=CISStatus.WAITING_FOR_ASSIGNMENT.value,
    )
    status = Column(String(16), nullable=False)
    priority = Column(String(64), nullable=False)
    remark = Column(String(), nullable=True)
    is_locked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    installment_no = Column(Integer, nullable=False)
