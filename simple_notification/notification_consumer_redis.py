from simple_notification.redis_ import redis_connection


async def consume(connected_clients):
    async with redis_connection.pubsub() as pubsub:
        await pubsub.subscribe('notifications')
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                notification_text = message["data"].decode()
                for client in connected_clients:
                    await client.send_text(notification_text)
