import asyncio
import os

import uvicorn
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from simple_notification.db import get_session
from simple_notification.models import User, UserCreate, Notification, NotificationCreate
from simple_notification.redis_ import redis_connection

# The FastAPI application object
app = FastAPI()

# Keeps track of WebSocket connections, which will receive real-time notifications
connected_clients = set()


@app.post('/users', response_model=User)
async def add_user(user_create: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(email=user_create.email)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@app.get('/notifications', response_model=list[Notification])
async def get_notifications(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Notification))
    notifications = result.scalars().all()
    return notifications


@app.post('/notifications', response_model=Notification)
async def add_notification(notification_create: NotificationCreate, session: AsyncSession = Depends(get_session)):
    notification = Notification(text=notification_create.text, user_id=notification_create.user_id)
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


# async def notification_consumer():
#     async with redis_connection.pubsub() as pubsub:
#         await pubsub.subscribe('notifications')
#         while True:
#             message = await pubsub.get_message(ignore_subscribe_messages=True)
#             if message:
#                 notification_text = message["data"].decode()
#                 for client in connected_clients:
#                     await client.send_text(notification_text)


import aiopg

async def notification_consumer_1():
    # Establish a connection pool to your PostgreSQL database
    dsn = 'dbname=simple_notification user=postgres password=postgres host=localhost'
    pool = await aiopg.create_pool(dsn)

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Set the name of the PostgreSQL channel to listen to
            channel_name = 'new_notification_channel'

            # Enable listening for notifications on the specified channel
            await cur.execute(f"LISTEN {channel_name}")

            while True:
                # Wait for notifications
                print('BEFORE call to `await conn.notifies.get`')
                msg = await conn.notifies.get()
                print('AFTER call to `await conn.notifies.get`')
                notification_text = msg.payload

                # Handle the notification (e.g., send it to connected clients)
                for client in connected_clients:
                    await client.send_text(notification_text)


import asyncpg



class Connection:
    def __init__(self, dsn):
        self.dsn = dsn
        self.connection = None
        self._notifies_queue = asyncio.Queue()

    async def connect(self):
        self.connection = await asyncpg.connect(self.dsn)
        await self.connection.add_listener("new_notification_channel", self._handle_notification_1)
        while True:
            await asyncio.sleep(1)

    async def execute(self, sql):
        return await self.connection.execute(sql)

    async def _handle_notification_1(self, pid, channel, payload, *args):
        print("_handle_notification!!!! \n ", f'{pid=}, {channel=}, {payload=}, {args=}')


async def notification_consumer_asyncpg():
    dsn = 'postgresql://postgres:postgres@localhost/simple_notification'
    conn = Connection(dsn)
    await conn.connect()


@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        # Keep the WebSocket connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


async def main():
    # Start the notification consumer in the background
    # asyncio.create_task(notification_consumer_asyncpg())
    # asyncio.create_task(notification_consumer_1())

    # Run the FastAPI application using uvicorn
    uvicorn_config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=int(os.environ['WEB_PORT'])
    )

    uvicorn_config.setup_event_loop()
    server = uvicorn.Server(config=uvicorn_config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
