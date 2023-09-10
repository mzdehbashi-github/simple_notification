import aiopg


async def consume(connected_clients):
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


