from typing import Optional
from datetime import datetime, timedelta

from fastapi import HTTPException, status, Cookie, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel

from simple_notification import db
from simple_notification.models.user import User

# To generate a string like this, run: `openssl rand -hex 32`
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def verify_password(raw_password, hashed_password):
    return pwd_context.verify(raw_password, hashed_password)


def get_password_hash(raw_password):
    return pwd_context.hash(raw_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=15)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_from_db(username: str) -> Optional[User]:
    session: AsyncSession
    async with db.get_connection() as session:
        statement = select(User).where(User.username == username).limit(1)
        result = await session.execute(statement)
        user = result.scalars().first()
    return user


async def authenticate_user(username: str, password: str) -> Optional[User]:
    user = await get_user_from_db(username)
    if user and verify_password(password, user.hashed_password):
        return user


async def _get_user_from_token(token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return await _get_user_from_token(token)


async def get_current_user_cookie(access_token: str = Cookie(None)) -> User:
    return await _get_user_from_token(access_token)
