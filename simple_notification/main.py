import asyncio
import os
import json

import uvicorn
import asyncpg
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, Cookie

from simple_notification import db
from simple_notification.routers import user, auth, notification
from simple_notification.auth import get_current_user_cookie
from simple_notification.models.user import User

# The FastAPI application object
app = FastAPI()
app.include_router(user.router)
app.include_router(notification.router)
app.include_router(
    auth.router,
    prefix='/auth',
    tags=['auth'],
)

# Keeps track of WebSocket connections, which will receive real-time notifications
connected_clients = {}

# Conducts Postgres notifications
pg_notifies = asyncio.Queue()


@app.get('/count-ws-connections', response_model=int)
async def count_ws_connections():
    print(connected_clients)
    return len(connected_clients)


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
        notification_detail = json.loads(payload)
        receiver_id = notification_detail['receiver_id']
        if client := connected_clients.get(receiver_id):
            await client.send_text(payload)


@app.websocket("/ws/notifications")
async def websocket_endpoint(
        websocket: WebSocket,
        access_token: str = Cookie(None),  # Extract the access_token from cookies
        user: User = Depends(get_current_user_cookie),
):
    await websocket.accept()
    connected_clients[user.id] = websocket

    try:
        # Keep the WebSocket connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        del connected_clients[user.id]


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
