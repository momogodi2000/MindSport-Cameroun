from django.test import TestCase

# Create your tests here.
import websockets
import asyncio
import json

async def test_websocket():
    async with websockets.connect(
        'ws://localhost:8000/ws/chat/1/?token=your_jwt_token'
    ) as websocket:
        # Send a message
        await websocket.send(json.dumps({
            'type': 'chat_message',
            'message': 'Hello WebSocket!'
        }))
        
        # Receive messages
        while True:
            response = await websocket.recv()
            print("Received:", response)

asyncio.get_event_loop().run_until_complete(test_websocket())