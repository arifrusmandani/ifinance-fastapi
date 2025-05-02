from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.src.database.models.user import User, UserType
from app.src.router.user.schema import UserCreateRequest, UserLoginRequest
import bcrypt
from jose import JWTError, jwt
from typing import Optional
from app.src.database.session import session_manager

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # TODO: Move to environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_password_hash(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verify the password
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class UserObject:
    @classmethod
    async def create_user(cls, user_data: UserCreateRequest) -> User:
        with session_manager() as db:
            user = User(
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                name=user_data.name,
                phone=user_data.phone,
                profile_picture=user_data.profile_picture,
                user_type=UserType.MEMBER
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[User]:
        with session_manager() as db:
            return db.query(User).filter(User.email == email).first()

    @classmethod
    async def authenticate_user(cls, login_data: UserLoginRequest) -> Optional[User]:
        with session_manager() as db:
            user = db.query(User).filter(
                User.email == login_data.email).first()
            if not user:
                return None
            if not verify_password(login_data.password, user.password_hash):
                return None
            return user

    @classmethod
    async def update_last_login(cls, user: User) -> None:
        with session_manager() as db:
            # Reattach the user to the current session
            user = db.merge(user)
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
