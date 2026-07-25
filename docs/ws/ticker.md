---
method: get
title: WebSocket Ticker
desc: A WebSocket endpoint that pushes a server-side ticker message at a configurable interval.
path: ws/ticker/{interval}
---

This is a WebSocket endpoint that pushes a JSON ticker message from the server every `interval` seconds, without requiring the client to send anything. It is intended for testing server-push handling (streaming, unsolicited messages) in WebSocket clients such as API Dash.

## Connection URL

Connect to the endpoint using the WebSocket scheme. Use `wss://` against the deployed (TLS) API, or `ws://` against a local server.

```
wss://api.apidash.dev/ws/ticker/2
```

When running the API locally:

```
ws://127.0.0.1:8000/ws/ticker/2
```

## Path Parameters

| Attribute | Data Type | Required | Description |
| ----------- | ----------- | ----------- | ----------- |
| `interval` | `integer` | Yes | Seconds between ticker messages. Must be between `1` and `60`. Values outside this range cause the server to close the connection with code `1008`. |

## Behavior

| Event | Result |
| ----------- | ----------- |
| Server timer (every `interval` s) | Server sends: `{"type": "ticker", "tick": <n>, "interval": <interval>}` |
| Client sends any message | Read and ignored (does not affect the ticker) |
| Invalid `interval` | Server closes with code `1008` |

`tick` starts at `1` and increments forever until the client disconnects.

## Sample Usage

### Example: Python (`websockets`)

```python
import asyncio
import websockets


async def main():
    async with websockets.connect("wss://api.apidash.dev/ws/ticker/2") as ws:
        for _ in range(3):
            print(await ws.recv())
        # {"type": "ticker", "tick": 1, "interval": 2}
        # {"type": "ticker", "tick": 2, "interval": 2}
        # {"type": "ticker", "tick": 3, "interval": 2}


asyncio.run(main())
```
