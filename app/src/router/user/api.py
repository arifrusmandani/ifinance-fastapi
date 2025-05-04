from fastapi import Security, Response, status as http_status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.src.database.models.user import User
from app.src.exception.handler.context import api_exception_handler
from app.src.router.user.object import UserObject, create_access_token
from app.src.router.user.schema import UserDetail, UserCreateRequest, UserLoginRequest, UserLoginResponse, UserResponse
from app.src.router.user.security import get_authorized_user, blacklist_token
from app.src.router.security import check_permission


router = InferringRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@cbv(router)
class UserView:
    """ User View Router"""
    res: Response
    user_object = UserObject

    @router.post("/register")
    async def register_user(
        self,
        request: UserCreateRequest
    ) -> dict:
        """
        Register a new user.

        - **email**: User's email address (must be unique)
        - **password**: User's password (minimum 8 characters)
        - **name**: User's full name
        - **phone**: User's phone number (optional)
        - **profile_picture**: URL to user's profile picture (optional)

        Returns the created user object without the password.
        """
        with api_exception_handler(self.res) as response_builder:
            data = await self.user_object.create_user(request)
            response_builder.status = True
            response_builder.code = http_status.HTTP_201_CREATED
            response_builder.message = "success"
            response_builder.data = jsonable_encoder(data)
        return response_builder.to_dict()

    @router.post("/login")
    async def login_user(
        self,
        form_data: OAuth2PasswordRequestForm = Depends()
    ) -> dict:
        """
        Login user and return access token.

        - **username**: User's email address
        - **password**: User's password

        Returns access token and user information.
        """
        with api_exception_handler(self.res) as response_builder:
            login_data = UserLoginRequest(
                email=form_data.username,
                password=form_data.password
            )

            user = await self.user_object.authenticate_user(login_data)
            if not user:
                response_builder.status = False
                response_builder.code = http_status.HTTP_401_UNAUTHORIZED
                response_builder.message = "Invalid email or password"
                return response_builder.to_dict()

            # Update last login
            await self.user_object.update_last_login(user)

            # Create access token
            access_token = create_access_token(
                data={"sub": user.email}
            )

            # Convert User model to UserBase
            user_base = UserDetail(
                id=user.id,
                email=user.email,
                name=user.name,
                phone=user.phone,
                profile_picture=user.profile_picture,
                user_type=user.user_type
            )

            # Prepare response
            login_response = UserLoginResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_base
            )

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "success"
            response_builder.data = jsonable_encoder(login_response)
        return response_builder.to_dict()

    @router.get("/me", response_model=UserResponse)
    async def read_users_me(
        self,
        authorized_user: User = Depends(get_authorized_user)
    ) -> dict:
        """
        Get current user data.

        Returns the current user's data based on the provided access token.
        """
        with api_exception_handler(self.res) as response_builder:
            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "success"
            response_builder.data = jsonable_encoder(authorized_user)
        return response_builder.to_dict()

    @router.post("/logout")
    async def logout_user(
        self,
        authorized_user: User = Depends(get_authorized_user),
        token: str = Depends(oauth2_scheme)
    ) -> dict:
        """
        Logout the current user and blacklist the token.

        This endpoint invalidates the current session by blacklisting the token.
        The token will be immediately invalid and cannot be used again.
        """
        with api_exception_handler(self.res) as response_builder:
            # Blacklist the token
            blacklist_token(token)
            
            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Successfully logged out"
            response_builder.data = None
        return response_builder.to_dict()
