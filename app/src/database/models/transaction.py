from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Enum, ForeignKey
import enum
from sqlalchemy.orm import relationship

from app.src.database import BaseModel


class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Transaction(BaseModel):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    type = Column(Enum(
        TransactionType, name='category_type_enum', create_type=False), nullable=False)
    category_code = Column(String(50))
    date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship
    user = relationship("User", back_populates="transactions")
