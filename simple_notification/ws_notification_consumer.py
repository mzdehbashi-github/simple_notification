import asyncio
import websockets


async def connect_to_websocket():
    uri = "ws://localhost:8000/ws/notifications"  # Replace with your WebSocket endpoint URL

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        try:
            while True:
                message = await websocket.recv()
                print(f"Received message from server: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect_to_websocket())
