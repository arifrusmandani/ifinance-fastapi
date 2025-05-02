from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.src.router.user.schema import UserCreate, UserResponse
from app.src.router.user.object import create_user, get_user_by_email


def register_user(db: Session, user: UserCreate) -> UserResponse:
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = create_user(db=db, user=user)
    return UserResponse.model_validate(new_user)
