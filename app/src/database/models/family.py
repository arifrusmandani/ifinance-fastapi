from sqlalchemy import Column, Integer, ForeignKey, Enum
import enum

from app.src.database import BaseModel

class EnumRelationship(enum.Enum):
    spouse = 'spouse'

class Family(BaseModel):
    __tablename__ = 'familys'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    family_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    relationship = Column(Enum(EnumRelationship), nullable=False)
