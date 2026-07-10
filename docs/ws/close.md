---
method: get
title: WebSocket Close With Code
desc: A WebSocket endpoint that closes the connection with a client-requested close code.
path: ws/close/{code}
---

This is a WebSocket endpoint for testing how clients handle server-initiated closes. On connect, the server sends one JSON message and then immediately closes the connection with the requested close code and a matching reason.

## Connection URL

Connect to the endpoint using the WebSocket scheme. Use `wss://` against the deployed (TLS) API, or `ws://` against a local server.

```
wss://api.foss42.com/ws/close/4001
```

When running the API locally:

```
ws://127.0.0.1:8000/ws/close/4001
```

## Path Parameters

| Attribute | Data Type | Required | Description |
| ----------- | ----------- | ----------- | ----------- |
| `code` | `integer` | Yes | The close code to close with. Allowed: `1000`–`1003`, `1007`–`1014`, `3000`–`4999`. Reserved / unsendable codes (e.g. `1005`, `1006`) are rejected by closing with `1008` instead. |

## Behavior

1. Server accepts the connection.
2. Server sends `{"type": "close", "message": "Closing with code <code>"}`.
3. Server closes with close code `<code>` and reason `Requested close with code <code>`.

## Sample Usage

### Example: Python (`websockets`)

```python
import asyncio
import websockets


async def main():
    try:
        async with websockets.connect("wss://api.foss42.com/ws/close/4001") as ws:
            print(await ws.recv())  # {"type": "close", "message": "Closing with code 4001"}
            await ws.recv()
    except websockets.exceptions.ConnectionClosed as e:
        print(e.rcvd.code, e.rcvd.reason)  # 4001 Requested close with code 4001


asyncio.run(main())
```
