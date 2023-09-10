import asyncio
import os

import uvicorn
import asyncpg
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from simple_notification import db
from simple_notification.models import User, UserCreate, Notification, NotificationCreate

# The FastAPI application object
app = FastAPI()

# Keeps track of WebSocket connections, which will receive real-time notifications
connected_clients = set()

# Conducts Postgres notifications
pg_notifies = asyncio.Queue()


@app.post('/users', response_model=User)
async def add_user(user_create: UserCreate, session: AsyncSession = Depends(db.get_session)):
    user = User(email=user_create.email)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@app.get('/notifications', response_model=list[Notification])
async def get_notifications(session: AsyncSession = Depends(db.get_session)):
    result = await session.execute(select(Notification))
    notifications = result.scalars().all()
    return notifications


@app.get('/count-ws-connections', response_model=int)
async def count_ws_connections():
    return len(connected_clients)


@app.post('/notifications', response_model=Notification)
async def add_notification(notification_create: NotificationCreate, session: AsyncSession = Depends(db.get_session)):
    notification = Notification(text=notification_create.text, user_id=notification_create.user_id)
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


async def handle_pg_notification(pid, channel, payload, notification: str):
    await pg_notifies.put(notification)


async def notification_consumer_asyncpg():
    connection = await asyncpg.connect(
        host=db.host,
        port=db.port,
        user=db.user,
        password=db.password,
        database=db.database,
    )

    await connection.add_listener("new_notification_channel", handle_pg_notification)

    while True:
        payload = await pg_notifies.get()

        # Handle the notification (e.g., send it to connected clients)
        for client in connected_clients:
            await client.send_text(payload)


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
    asyncio.create_task(notification_consumer_asyncpg())

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
