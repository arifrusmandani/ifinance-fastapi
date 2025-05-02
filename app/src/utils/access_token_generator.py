import json
from contextlib import asynccontextmanager
from app.src.utils.httpx_client import httpx_context
from app.src.core.config import ORGANIZATION_SERVICE_URL


class AccessTokenGenerator:
    @classmethod
    async def get_access_token(cls, app_code):
        url = ORGANIZATION_SERVICE_URL+"/external_party/{}/access_token".format(app_code)
        async with httpx_context() as client:
            response = await client.get(url)
            response = response.json()
            if not response.get('status'):
                raise FileNotFoundError("Token not found")
        return response.get('data').get('access_token')
