from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.src.database import BaseModel


class EnumRelationship(enum.Enum):
    spouse = 'spouse'

class Family(BaseModel):
    __tablename__ = 'Familys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    family_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    relationship = Column(Enum(EnumRelationship), nullable=False)

    # Relationships
    user = relationship('User', foreign_keys=[user_id])
    family_user = relationship('User', foreign_keys=[family_user_id])
