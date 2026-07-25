---
method: get
title: WebSocket Broadcast
desc: A chat-style WebSocket endpoint that broadcasts every message to all connected clients.
path: ws/broadcast
---

This is a chat-style ("fan-out") WebSocket endpoint: every text message sent by any connected client is broadcast to **all** currently connected clients, including the sender. It is intended for testing multiple simultaneous connections (e.g. multiple tabs/windows of a WebSocket client such as API Dash).

## Connection URL

Connect to the endpoint using the WebSocket scheme. Use `wss://` against the deployed (TLS) API, or `ws://` against a local server.

```
wss://api.apidash.dev/ws/broadcast
```

When running the API locally:

```
ws://127.0.0.1:8000/ws/broadcast
```

## Behavior

1. Client A and Client B connect.
2. Client A sends `hello everyone`.
3. Both Client A and Client B receive `hello everyone`.

Messages are relayed unchanged. Clients that have disconnected are dropped from the broadcast set.

## Sample Usage

### Example: Python (`websockets`), two clients

```python
import asyncio
import websockets

URL = "wss://api.apidash.dev/ws/broadcast"


async def main():
    async with websockets.connect(URL) as a, websockets.connect(URL) as b:
        await a.send("hello everyone")
        print(await a.recv())  # hello everyone
        print(await b.recv())  # hello everyone


asyncio.run(main())
```
