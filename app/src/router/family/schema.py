from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.src.router.response import BaseListResponse, BaseResponse
from app.src.database.models.family import EnumRelationship


class FamilyMemberDetail(BaseModel):
    family_user_id: int
    email: str
    name: str
    phone: Optional[str] = None
    last_login: Optional[datetime] = None
    is_active: bool
    relationship: EnumRelationship
    is_verified: bool


class FamilyListResponse(BaseListResponse):
    data: List[FamilyMemberDetail] = []


class AddFamilyMemberRequest(BaseModel):
    email: EmailStr
    relationship: EnumRelationship


class FamilyDetailResponse(BaseResponse):
    data: Optional[FamilyMemberDetail] = None
