from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
import enum
from sqlalchemy.orm import relationship

from app.src.database import BaseModel


class UserType(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    phone = Column(String(20))
    profile_picture = Column(Text)
    user_type = Column(Enum(UserType, name='user_type_enum', create_type=False),
                       default=UserType.MEMBER)
    gemini_api_key = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationship
    transactions = relationship("Transaction", back_populates="user")
