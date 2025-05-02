from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.src.database import BaseModel
from app.src.database.models.user import User


class Member(BaseModel):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    member_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    user = relationship('User', foreign_keys=[user_id])
    member_user = relationship('User', foreign_keys=[member_user_id])
