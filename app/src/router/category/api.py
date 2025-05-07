from fastapi import APIRouter, Depends, Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status as http_status
from fastapi.encoders import jsonable_encoder

from app.src.database.models.user import User
from app.src.database.models.transaction import TransactionType
from app.src.router.category.object import CategoryObject
from app.src.router.category.schema import CategoryListResponse
from app.src.router.user.security import get_authorized_user
from app.src.exception.handler.context import api_exception_handler


router = InferringRouter()


@cbv(router)
class CategoryView:
    """ Category View Router """
    res: Response

    def __init__(self, authorized_user: User = Depends(get_authorized_user)):
        self.authorized_user = authorized_user
        self.category_object = CategoryObject(authorized_user)

    @router.get("/", response_model=CategoryListResponse)
    async def get_categories(
        self,
        type: TransactionType = None
    ) -> dict:
        """
        Get all categories, optionally filtered by type.

        - **type**: Filter categories by type (INCOME/EXPENSE)

        Returns a list of categories.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            categories = await self.category_object.get_categories(category_type=type)
            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Categories retrieved successfully"
            response_builder.data = jsonable_encoder(categories)
            return response_builder.to_dict()
