import json
import re
from app.src.database.session import session_manager
from app.src.database.models.user import User  # Import User
from app.src.router.ai.crud import ai_analysis_crud
# Import LatestFinancialAnalysis
from app.src.router.ai.schema import AIAnalysisCreate, LatestFinancialAnalysis
# Import AIAnalysis and AnalysisType
from app.src.database.models.ai_analysis import AIAnalysis, AnalysisType
from typing import Optional  # Import Optional
from sqlalchemy import desc  # Import desc


class AIObject:
    """ AI Object """

    def __init__(self, authorized_user: User):
        self.authorized_user = authorized_user
        self.crud_ai_analysis = ai_analysis_crud

    async def save_analysis_result(
        self,
        analysis_type: AnalysisType,
        input_data: str,
        result: str
    ):
        with session_manager() as db:
            analysis_data = AIAnalysisCreate(
                user_id=self.authorized_user.id,
                analysis_type=analysis_type,
                input_data=input_data,
                result=result
            )
            await self.crud_ai_analysis.create(db, analysis_data)
            # Optionally, you can return the created analysis object if needed
            # return created_analysis

    async def get_latest_analysis(self) -> Optional[LatestFinancialAnalysis]:
        """Get the latest AI analysis result for the authorized user."""
        with session_manager() as db:
            # Query the AIAnalysis table for the latest record for the user
            latest_analysis = db.query(AIAnalysis)
            latest_analysis = latest_analysis.filter(
                AIAnalysis.user_id == self.authorized_user.id)
            latest_analysis = latest_analysis.order_by(
                desc(AIAnalysis.created_at))
            latest_analysis = latest_analysis.first()

            if not latest_analysis:
                raise FileNotFoundError("Data Not Found")

            # Map the SQLAlchemy model to the Pydantic schema
            return LatestFinancialAnalysis(
                analysis_type=latest_analysis.analysis_type,
                input_data=latest_analysis.input_data,
                result=latest_analysis.result,
                created_at=latest_analysis.created_at
            )


    def parse_ai_json_response(self, raw_response):
        # Hapus blok kode markdown seperti ```json ... ```
        cleaned = re.sub(r"^```json|```$", "", raw_response.strip(), flags=re.MULTILINE).strip()
        
        # Decode escape sequences seperti \n, \"
        try:
            cleaned = bytes(cleaned, "utf-8").decode("unicode_escape")
        except Exception as e:
            print("Unicode decode warning:", e)
        
        # Final parsing
        return json.loads(cleaned)