import google.generativeai as genai
from google import genai
from fastapi import HTTPException, Response, status as http_status, Security
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from app.src.core.config import GEMINI_API_KEY
from app.src.exception.handler.context import api_exception_handler
from app.src.router.ai.schema import PromptRequest

router = InferringRouter()
# genai.configure(api_key=GEMINI_API_KEY)

# model = genai.GenerativeModel("gemini-pro")
client = genai.Client(api_key=GEMINI_API_KEY)

@cbv(router)
class CustomerView:
    res: Response

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
