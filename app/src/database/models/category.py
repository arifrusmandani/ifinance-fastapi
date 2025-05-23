from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
import enum

from app.src.database import BaseModel
from app.src.database.models.transaction import TransactionType


class Category(BaseModel):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    type = Column(Enum(
        TransactionType, name='category_type_enum', create_type=False), nullable=False)
    icon = Column(String(50))
    color = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
