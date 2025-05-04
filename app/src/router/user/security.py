from datetime import datetime, timedelta
from typing import Optional, Set
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

# In-memory blacklist
blacklisted_tokens: Set[str] = set()

security = HTTPBearer()

def blacklist_token(token: str) -> None:
    """Add token to blacklist"""
    blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return token in blacklisted_tokens

def create_expired_token(data: dict) -> str:
    """Create an immediately expired token"""
    to_encode = data.copy()
    # Set expiration to 1 second ago
    expire = datetime.utcnow() - timedelta(seconds=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify the JWT token and return the token string.
    Raises HTTPException if token is invalid or blacklisted.
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return token
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
