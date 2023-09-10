import asyncio
import websockets


async def open_websockets(num_ws_clients, ws_endpoint):
    async def ws_client(number):
        async with websockets.connect(ws_endpoint) as websocket:
            while True:
                message = await websocket.recv()
                print(f"Connection number {number} received message: {message}")

    tasks = []
    for number in range(num_ws_clients):
        tasks.append(ws_client(number))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    num_ws_clients = 500
    ws_endpoint = "ws://localhost:8000/ws/notifications"

    asyncio.get_event_loop().run_until_complete(open_websockets(num_ws_clients, ws_endpoint))
