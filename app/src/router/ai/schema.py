from pydantic import BaseModel
from typing import Optional
from app.src.router.response import BaseResponse
from app.src.database.models.ai_analysis import AnalysisType
from datetime import datetime


class PromptRequest(BaseModel):
    prompt: str


# Add the new schema for financial analysis response
class FinancialAnalysisResponse(BaseResponse):
    data: Optional[dict] = None


# Add schema for creating AI analysis record
class AIAnalysisCreate(BaseModel):
    user_id: int
    analysis_type: AnalysisType
    input_data: str
    result: dict


# Add schema for getting latest AI analysis
class LatestFinancialAnalysis(BaseModel):
    analysis_type: AnalysisType
    input_data: str
    result: dict
    created_at: datetime


class LatestFinancialAnalysisResponse(BaseResponse):
    data: Optional[LatestFinancialAnalysis] = None
