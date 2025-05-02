from fastapi import APIRouter

router = APIRouter()


@router.get("/", include_in_schema=True)
async def index():
    return "ok"


@router.get("/healthz", include_in_schema=False)
async def healthz():
    return "ok"