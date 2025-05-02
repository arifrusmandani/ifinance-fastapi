from fastapi import FastAPI
from uvicorn import run
from app.src.router.api import router
from app.src.router.root.api import router as root_router
from app.src.core import config
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from app.src.exception.handler import http_error, validation_error


def get_application():
    """
    generate configured fastapi instance

    :param:
    :return: FastAPI instance

    Example:
        >>> app = get_application()
        >>> isinstance(app, FastAPI)
        True
    """
    application = FastAPI(
        title=config.PROJECT_NAME,
        docs_url=f"{config.API_PREFIX}/docs",
        openapi_url=f"{config.API_PREFIX}/openapi.json"
    )
    application.include_router(router, prefix=config.API_PREFIX)
    application.include_router(root_router, tags=["root"], prefix="")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(HTTPException, http_error.http_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error.http422_error_handler)

    return application


app = get_application()


if __name__ == '__main__':
    run(app=app)
