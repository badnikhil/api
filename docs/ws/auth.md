---
method: get
title: WebSocket Auth Echo
desc: A token-gated WebSocket echo endpoint accepting a Bearer header or a token query parameter.
path: ws/auth
---

This is a token-gated echo endpoint for testing authenticated WebSocket connections. The mock token is public and not a secret:

```
apidash-test-ws-token
```

Authenticate in either of two ways:

1. **Header** (for clients that support custom connection headers): `Authorization: Bearer apidash-test-ws-token`
2. **Query parameter** (works from browsers too): `?token=apidash-test-ws-token`

## Connection URL

Connect to the endpoint using the WebSocket scheme. Use `wss://` against the deployed (TLS) API, or `ws://` against a local server.

```
wss://api.foss42.com/ws/auth?token=apidash-test-ws-token
```

When running the API locally:

```
ws://127.0.0.1:8000/ws/auth?token=apidash-test-ws-token
```

## Behavior

| Event | Result |
| ----------- | ----------- |
| Valid token (header or query param) | Server sends `{"type": "auth", "status": "authenticated"}`, then echoes every text message back unchanged |
| Missing or invalid token | Connection is accepted, then immediately closed with code `1008` and reason `Missing or invalid token` |

## Sample Usage

### Example #1: Python (`websockets`), header auth

```python
import asyncio
import websockets


async def main():
    async with websockets.connect(
        "wss://api.foss42.com/ws/auth",
        additional_headers={"Authorization": "Bearer apidash-test-ws-token"},
    ) as ws:
        print(await ws.recv())  # {"type": "auth", "status": "authenticated"}
        await ws.send("hello")
        print(await ws.recv())  # hello


asyncio.run(main())
```

### Example #2: JavaScript (browser `WebSocket`), query param auth

```javascript
const ws = new WebSocket("wss://api.foss42.com/ws/auth?token=apidash-test-ws-token");

ws.onmessage = (event) => console.log(event.data); // {"type": "auth", "status": "authenticated"}
```
