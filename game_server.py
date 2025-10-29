import asyncio
import websockets
import json

clients = {}

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        username = data["username"]
        clients[username] = websocket

        if "invite" in data:
            opponent = data["invite"]
            if opponent in clients:
                await clients[opponent].send(f"{username} has invited you to a game!")
                await websocket.send(f"Invite sent to {opponent}")
            else:
                await websocket.send(f"{opponent} is not online.")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("🎮 Multiplayer server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
