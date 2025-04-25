import asyncio
import json
import os
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
import websockets


USERS = {}  # websocket -> {"name": str, "room": str}
ROOMS = {}  # room -> set of websockets
CONNECTION_META = {}  # websocket -> {"name": str, "room": str}


def get_history_file(room):
    return f"chat_history_{room}.json"


def load_history(room):
    try:
        with open(get_history_file(room), "r") as f:
            return json.load(f)
    except:
        return []


def save_message(room, message):
    history = load_history(room)
    history.append(message)
    with open(get_history_file(room), "w") as f:
        json.dump(history, f)


def clear_history(room):
    with open(get_history_file(room), "w") as f:
        json.dump([], f)


class ReuseTCPServer(TCPServer):
    allow_reuse_address = True


def start_http_server():
    os.chdir("static")
    with ReuseTCPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler) as httpd:
        print("✨ HTTP server running at http://localhost:8000")
        httpd.serve_forever()


async def notify_users(room):
    names = [u["name"] for u in USERS.values() if u["room"] == room]
    message = json.dumps({"type": "users", "users": names})
    for ws in ROOMS.get(room, []):
        try:
            await ws.send(message)
        except:
            pass


async def websocket_handler(websocket, path):
    parsed = urlparse(path)
    params = parse_qs(parsed.query)
    username = params.get("name", ["Anonymous"])[0]
    room = params.get("room", ["main"])[0]

    print(f"🧝 {username} joined room: {room}")
    USERS[websocket] = {"name": username, "room": room}
    ROOMS.setdefault(room, set()).add(websocket)

    await websocket.send(json.dumps({"type": "history", "messages": load_history(room)}))

    join_msg = {
        "type": "message",
        "user": "System",
        "text": f"{username} joined the chat.",
        "time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    }
    await broadcast(room, json.dumps(join_msg))
    save_message(room, join_msg)
    await notify_users(room)

    try:
        async for raw in websocket:
            data = json.loads(raw)

            if data.get("text") == "/clear":
                clear_history(room)
                await broadcast(room, json.dumps({"type": "clear"}))
                continue

            msg = {
                "type": "message",
                "user": username,
                "text": data["text"],
                "time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            }
            save_message(room, msg)
            await broadcast(room, json.dumps(msg), exclude=websocket)
    except:
        pass
    finally:
        ROOMS[room].remove(websocket)
        USERS.pop(websocket, None)
        print(f"🚪 {username} left room: {room}")
        leave_msg = {
            "type": "message",
            "user": "System",
            "text": f"{username} left the chat.",
            "time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        }
        await broadcast(room, json.dumps(leave_msg))
        save_message(room, leave_msg)
        await notify_users(room)


async def broadcast(room, message, exclude=None):
    for client in list(ROOMS.get(room, [])):
        if client != exclude:
            try:
                await client.send(message)
            except:
                pass


async def main():
    threading.Thread(target=start_http_server, daemon=True).start()
    try:
        async with websockets.serve(websocket_handler, host="0.0.0.0", port=3000):
            print("📱 WebSocket server running at ws://localhost:3000")
            await asyncio.Future()  # Keeps server alive
    except asyncio.CancelledError:
        pass  # Silently ignore cancellation


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Server stopped.")
