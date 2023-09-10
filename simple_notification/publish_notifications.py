import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from simple_notification.db import engine
from simple_notification.models import Notification
from simple_notification.redis_ import redis_connection


batch_size = 10
channel_name = 'notifications'


async def _process_notification(notification: Notification):
    await redis_connection.publish(channel_name, notification.text)
    notification.is_published = True


async def publish_notifications():
    """
    Reads `Notification` records from DB and publish them into the related channel on redis pub-sub.

    For better performance, all records are processed concurrently.

    This module should be ran periodically, e.g. using `cron` command.
    """

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Use the session to query and lock a batch of records
        query = select(Notification).where(Notification.is_published == False).limit(batch_size).with_for_update()
        result = await session.execute(query)
        notifications = result.scalars().all()
        if notifications:
            tasks = [_process_notification(notification) for notification in notifications]

            await asyncio.gather(*tasks)

            # Batch update the records in the database
            await session.commit()


if __name__ == "__main__":
    asyncio.run(publish_notifications())
