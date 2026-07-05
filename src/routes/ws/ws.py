import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

ws_router = APIRouter(tags=["WebSockets"])


@ws_router.websocket("/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break
            if message.get("bytes") is not None:
                # Echo binary frames back unchanged.
                await websocket.send_bytes(message["bytes"])
                continue
            data = message.get("text", "")
            try:
                # If it's valid JSON, echo it back as text (re-serialized).
                json_data = json.loads(data)
                await websocket.send_text(json.dumps(json_data))
            except json.JSONDecodeError:
                # Otherwise, echo the raw string unchanged.
                await websocket.send_text(data)
    except WebSocketDisconnect:
        pass

@ws_router.websocket("/heartbeat")
async def websocket_heartbeat(websocket: WebSocket):
    await websocket.accept()
    
    async def send_heartbeat():
        try:
            while True:
                await asyncio.sleep(5)
                await websocket.send_json({"type": "heartbeat", "message": "ping"})
        except asyncio.CancelledError:
            pass

    async def receive_messages():
        try:
            while True:
                try:
                    data = await websocket.receive_json()
                    if data.get("message") == "ping":
                        await websocket.send_json({"type": "heartbeat", "message": "pong"})
                    else:
                        await websocket.send_json({"type": "message", "data": data})
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON"})
        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            pass

    heartbeat_task = asyncio.create_task(send_heartbeat())
    receive_task = asyncio.create_task(receive_messages())
    
    done, pending = await asyncio.wait(
        [heartbeat_task, receive_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    
    for task in pending:
        task.cancel()

@ws_router.websocket("/ticker/{interval}")
async def websocket_ticker(websocket: WebSocket, interval: int):
    """Pushes a ticker message from the server every `interval` seconds (1-60)."""
    await websocket.accept()
    if interval < 1 or interval > 60:
        await websocket.close(code=1008, reason="interval must be between 1 and 60 seconds")
        return

    async def send_ticks():
        tick = 0
        try:
            while True:
                await asyncio.sleep(interval)
                tick += 1
                await websocket.send_json({"type": "ticker", "tick": tick, "interval": interval})
        except asyncio.CancelledError:
            pass

    async def receive_messages():
        try:
            while True:
                # Drain incoming frames so client disconnects are detected promptly.
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            pass

    ticker_task = asyncio.create_task(send_ticks())
    receive_task = asyncio.create_task(receive_messages())

    done, pending = await asyncio.wait(
        [ticker_task, receive_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()


@ws_router.websocket("/close/{code}")
async def websocket_close(websocket: WebSocket, code: int):
    """Accepts the connection, sends one message and closes with the requested close code."""
    await websocket.accept()
    valid = (1000 <= code <= 1003) or (1007 <= code <= 1014) or (3000 <= code <= 4999)
    if not valid:
        await websocket.close(code=1008, reason="Unsupported close code")
        return
    try:
        await websocket.send_json({"type": "close", "message": f"Closing with code {code}"})
        await websocket.close(code=code, reason=f"Requested close with code {code}")
    except WebSocketDisconnect:
        pass


WS_AUTH_TOKEN = "apidash-test-ws-token"

@ws_router.websocket("/auth")
async def websocket_auth(websocket: WebSocket):
    """
    A token-gated echo endpoint. Authenticate with either
    an `Authorization: Bearer apidash-test-ws-token` header or
    a `?token=apidash-test-ws-token` query parameter.
    Invalid or missing tokens get closed with code 1008.
    """
    await websocket.accept()
    auth_header = websocket.headers.get("authorization")
    query_token = websocket.query_params.get("token")
    authenticated = (auth_header == f"Bearer {WS_AUTH_TOKEN}") or (query_token == WS_AUTH_TOKEN)
    if not authenticated:
        await websocket.close(code=1008, reason="Missing or invalid token")
        return
    try:
        await websocket.send_json({"type": "auth", "status": "authenticated"})
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass


broadcast_clients: set = set()

@ws_router.websocket("/broadcast")
async def websocket_broadcast(websocket: WebSocket):
    """
    A chat-style endpoint: every message sent by any client is
    broadcast to all currently connected clients (including the sender).
    """
    await websocket.accept()
    broadcast_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in list(broadcast_clients):
                try:
                    await client.send_text(data)
                except Exception:
                    broadcast_clients.discard(client)
    except WebSocketDisconnect:
        pass
    finally:
        broadcast_clients.discard(websocket)


@ws_router.websocket("/timeout/{timeout}")
async def websocket_strict_heartbeat(websocket: WebSocket, timeout: int):
    await websocket.accept()
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=timeout)
                if data.get("message") == "ping":
                    await websocket.send_json({"type": "heartbeat", "message": "pong"})
                else:
                    await websocket.send_json({"type": "message", "data": data})
            except asyncio.TimeoutError:
                await websocket.close(code=1008, reason="Heartbeat timeout")
                break
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    except WebSocketDisconnect:
        pass
