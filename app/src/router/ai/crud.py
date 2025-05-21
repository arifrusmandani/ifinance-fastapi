from sqlalchemy.orm import Session
from app.src.base.crud import CRUDBase
from app.src.database.models.ai_analysis import AIAnalysis
from app.src.router.ai.schema import AIAnalysisCreate


class CRUDAIAnalysis(CRUDBase[AIAnalysis, AIAnalysisCreate, None]):
    pass


ai_analysis_crud = CRUDAIAnalysis(AIAnalysis)
