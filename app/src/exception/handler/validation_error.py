from typing import Union

from fastapi.exceptions import RequestValidationError
from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import validation_error_response_definition
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from app.src.utils.response_builder import ResponseBuilder
from starlette import status


async def http422_error_handler(
    _: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    response = ResponseBuilder()
    message = ""
    for i, error in enumerate(exc.errors()):
        if len(exc.errors()) == i + 1:
            # message += f'{error["msg"]} {error["loc"][1]}'
            message += f'{error["msg"]}'
        else:
            # message += f'{error["msg"]} {error["loc"][1]}' + ", "
            message += f'{error["msg"]}' + ", "
    response.add_attribute("status")
    response.update_value("status", False)
    response.update_value("message", message)
    response.update_value("code", status.HTTP_400_BAD_REQUEST)
    return JSONResponse(response.to_dict(), status_code=status.HTTP_400_BAD_REQUEST)


validation_error_response_definition["properties"] = {
    "errors": {
        "title": "Errors",
        "type": "array",
        "items": {"$ref": "{0}ValidationError".format(REF_PREFIX)},
    }
}