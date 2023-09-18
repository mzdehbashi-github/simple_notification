from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from simple_notification.models import User, UserCreate
from simple_notification.auth import get_password_hash
from simple_notification import db


router = APIRouter()


@router.post('/users', response_model=User, response_model_include={'id', 'username'})
async def add_user(
        user_create: UserCreate,
        session: AsyncSession = Depends(db.get_session)
):
    user = User(
        username=user_create.username,
        hashed_password=get_password_hash(user_create.raw_password)
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
