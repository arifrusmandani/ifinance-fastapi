from fastapi import APIRouter, Depends, Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status as http_status
from fastapi.encoders import jsonable_encoder

from app.src.database.models.user import User
from app.src.router.family.object import FamilyObject
from app.src.router.family.schema import FamilyListResponse, AddFamilyMemberRequest, FamilyMemberDetail, FamilyDetailResponse
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
        - is_verified
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            family_members, total_count = await self.family_object.get_family_members()

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Family members retrieved successfully"
            response_builder.data = jsonable_encoder(family_members)
            response_builder.record_count = total_count
        return response_builder.to_dict()

    @router.post("/", response_model=FamilyDetailResponse)
    async def add_family_member(self, request: AddFamilyMemberRequest) -> dict:
        """
        Add a new family member.

        - **email**: Email of the user to add as family member
        - **relationship**: Relationship type between the users (e.g., spouse)

        Returns the added family member details.
        """
        with api_exception_handler(self.res) as response_builder:
            family_member = await self.family_object.add_family_member(
                email=request.email,
                relationship=request.relationship
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_201_CREATED
            response_builder.message = "Family member added successfully"
            response_builder.data = jsonable_encoder(family_member)
        return response_builder.to_dict()

    @router.put("/{family_user_id}/verify", response_model=FamilyDetailResponse)
    async def verify_family_member(self, family_user_id: int) -> dict:
        """
        Verify family member relationship.
        This endpoint can only be called by the family member to verify their relationship with the main user.

        - **family_user_id**: ID of the main user (the user who added the family member)

        Returns the updated family member details with is_verified set to true.
        """
        with api_exception_handler(self.res) as response_builder:
            family_member = await self.family_object.verify_family_member(
                family_user_id=family_user_id
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Family member verified successfully"
            response_builder.data = jsonable_encoder(family_member)
        return response_builder.to_dict()
