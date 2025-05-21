from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.src.database import BaseModel


class AnalysisType(enum.Enum):
    spending_pattern = 'spending_pattern'
    savings_recommendation = 'savings_recommendation'
    budget_planning = 'budget_planning'
    general = 'general'


class AIAnalysis(BaseModel):
    __tablename__ = 'ai_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    input_data = Column(Text, nullable=False)
    result = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user = relationship('User')
