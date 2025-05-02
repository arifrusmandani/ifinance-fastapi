from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.database.session import session_manager
from app.src.database.models.user import User
from app.src.router.user.object import UserObject

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # TODO: Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify the JWT token and return the token string.
    Raises HTTPException if token is invalid.
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


async def get_current_user(token: str = Depends(verify_token)) -> User:
    """
    Get the current user from the JWT token.
    Raises HTTPException if user is not found or token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    
    user = await UserObject.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    Raises HTTPException if user is not active.
    """
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_authorized_user(user: User = Depends(get_current_active_user)) -> User:
    """
    Get the authorized user with all necessary checks.
    This is the main dependency to use in protected endpoints.
    """
    return user
