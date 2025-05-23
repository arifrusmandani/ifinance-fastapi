from google import genai
import json  # Import json for data formatting

from fastapi import HTTPException, Response, status as http_status, Security, Depends  # Add Depends
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from datetime import date  # Import date
from typing import Optional, Dict, Any  # Import types

# Import TEMPLATE_PROMPT_ANALYSIS
from app.src.core.config import GEMINI_API_KEY, JSON_FORMAT, TEMPLATE_PROMPT_ANALYSIS, TEMPLATE_PROMPT_ANALYSIS_JSON
from app.src.exception.handler.context import api_exception_handler
# Keep if still needed for /ask-gemini
from app.src.router.ai.schema import PromptRequest, FinancialAnalysisResponse, LatestFinancialAnalysisResponse
from app.src.router.report.object import ReportObject  # Import ReportObject
from app.src.database.models.user import User
from app.src.router.user.security import get_authorized_user  # Import User for Depends
from app.src.router.ai.object import AIObject  # Import AIObject
from app.src.database.models.ai_analysis import AnalysisType  # Import AnalysisType

router = InferringRouter()
client = genai.Client(api_key=GEMINI_API_KEY)


@cbv(router)
class AIView:
    """ AI View Router """
    res: Response

    # Remove the old /ask-gemini endpoint or keep it if still needed
    @router.post("/ask-gemini")
    async def analyze_report(
        self,
        data: PromptRequest
    ) -> dict:
        with api_exception_handler(self.res) as response_builder:
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash", contents=data.prompt
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            response_builder.status = True
            response_builder.code = http_status.HTTP_201_CREATED
            response_builder.message = "success"
            response_builder.data = response.text
        return response_builder.to_dict()

    @router.get("/analyze-financial", response_model=FinancialAnalysisResponse)
    async def analyze_financial(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        authorized_user: User = Depends(get_authorized_user)
    ) -> dict:
        """
        Analyze financial cashflow data using AI.

        - **start_date**: Start date for cashflow data filter (optional)
        - **end_date**: End date for cashflow data filter (optional)

        Returns the AI-generated financial analysis report.
        """
        with api_exception_handler(self.res) as response_builder:
            try:
                # Get cashflow data
                report_object = ReportObject(authorized_user)
                cashflow_data = await report_object.get_cashflow_data(
                    user_id=authorized_user.id,
                    start_date=start_date,
                    end_date=end_date
                )

                # Format data as JSON
                json_data = json.dumps(
                    jsonable_encoder(cashflow_data), indent=2)

                # Build the prompt
                prompt = TEMPLATE_PROMPT_ANALYSIS_JSON.format(
                    json_data=json_data,
                    json_format=json.dumps(JSON_FORMAT, indent=2)
                )

                # Call the AI model
                # Use a suitable model, e.g., "gemini-pro" or "gemini-1.5-flash-latest"
                # Check available models and their capabilities/costs
                ai_response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )

                raw_response = ai_response.text

                ai_object = AIObject(authorized_user)
                try:
                    result = ai_object.parse_ai_json_response(raw_response)
                except json.JSONDecodeError as e:
                    print("JSON Error:", e)
                except Exception as e:
                    print("General Error:", e)

                # Save analysis result
                await ai_object.save_analysis_result(
                    analysis_type=AnalysisType.general,
                    input_data="",  # Empty as requested
                    result=result
                )

            except Exception as e:
                # Log the error for debugging
                print(f"Error generating financial analysis: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Error generating analysis: {e}")

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Financial analysis generated successfully"
            response_builder.data = result  # Return the text response
        return response_builder.to_dict()

    @router.get("/latest-analysis", response_model=LatestFinancialAnalysisResponse)
    async def get_latest_analysis(
        self,
        authorized_user: User = Depends(get_authorized_user)
    ) -> dict:
        """
        Get the latest AI financial analysis for the current user.

        Returns the latest AI analysis result.
        """
        with api_exception_handler(self.res) as response_builder:
            ai_object = AIObject(authorized_user)
            latest_analysis = await ai_object.get_latest_analysis()

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Latest financial analysis retrieved successfully"
            response_builder.data = jsonable_encoder(latest_analysis)
        return response_builder.to_dict()
