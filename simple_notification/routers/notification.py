from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from simple_notification.models import Notification, NotificationCreate
from simple_notification.auth import get_current_user
from simple_notification.models.user import User
from simple_notification import db


router = APIRouter()


@router.get(
    '/notifications',
    response_model=list[Notification],
    dependencies=[Depends(get_current_user)]
)
async def get_notifications(
        session: AsyncSession = Depends(db.get_session),
):
    result = await session.execute(select(Notification))
    notifications = result.scalars().all()
    return notifications


@router.post('/notifications', response_model=Notification)
async def add_notification(
        notification_create: NotificationCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: AsyncSession = Depends(db.get_session),
):

    notification = Notification(
        text=notification_create.text,
        sender_id=current_user.id,
        receiver_id=notification_create.receiver_id,
    )

    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification
