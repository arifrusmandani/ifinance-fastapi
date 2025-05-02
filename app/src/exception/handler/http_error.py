from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.src.utils.response_builder import ResponseBuilder

async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    response = ResponseBuilder()
    response.message = exc.detail
    response.status = False
    response.code = exc.status_code
    return JSONResponse(response.to_dict(), status_code=exc.status_code)
