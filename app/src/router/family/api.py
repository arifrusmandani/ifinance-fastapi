from fastapi import APIRouter, Depends, Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status as http_status
from fastapi.encoders import jsonable_encoder

from app.src.database.models.user import User
from app.src.router.family.object import FamilyObject
from app.src.router.family.schema import FamilyListResponse
from app.src.router.user.security import get_authorized_user
from app.src.exception.handler.context import api_exception_handler

router = InferringRouter()


@cbv(router)
class FamilyView:
    """ Family View Router """
    res: Response

    def __init__(self, authorized_user: User = Depends(get_authorized_user)):
        self.authorized_user = authorized_user
        self.family_object = FamilyObject(authorized_user)

    @router.get("/", response_model=FamilyListResponse)
    async def get_family_members(self) -> dict:
        """
        Get all family members for the current user.

        Returns a list of family members with their details including:
        - family_user_id
        - email
        - name
        - phone
        - last_login
        - is_active
        - relationship
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            family_members, total_count = await self.family_object.get_family_members()

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Family members retrieved successfully"
            response_builder.data = jsonable_encoder(family_members)
            response_builder.record_count = total_count
        return response_builder.to_dict()
