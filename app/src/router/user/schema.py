from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime
from app.src.database.models.user import User, UserType
from app.src.router.response import BaseListResponse, BaseResponse



class UserBase(BaseModel):
    email: EmailStr
    name: constr(min_length=1, max_length=100)
    phone: Optional[constr(max_length=20)] = None
    profile_picture: Optional[str] = None

class UserDetail(UserBase):
    user_type: Optional[str] = None


class UserCreateRequest(UserBase):
    password: constr(min_length=8)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserDetail

    class Config:
        from_attributes = True


class UserResponse(BaseResponse):
    data: Optional[UserDetail] = None

    