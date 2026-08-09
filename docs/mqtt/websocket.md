---
protocol: mqtt
title: MQTT over WebSocket
desc: The broker also accepts MQTT over WebSocket at ws://localhost:9001, for browser-based and web MQTT clients.
path: mqtt/websocket
---

In addition to plain MQTT over TCP on port `1883`, the broker exposes **MQTT
over WebSocket** on port `9001`. This is what browser-based MQTT clients (and
API Dash's web build) use, since browsers cannot open raw TCP sockets.

Both listeners talk to the same broker, so a message published over TCP is
received over WebSocket and vice versa.

## Endpoint

```
ws://localhost:9001
```

Use `mqtt://localhost:1883` for the TCP transport (see the
[overview](README.md)).

## Behavior

| Transport | URL | Notes |
| ----------- | ----------- | ----------- |
| TCP | `mqtt://localhost:1883` | Native MQTT clients |
| WebSocket | `ws://localhost:9001` | Browser / web clients; same broker, same topics |

All scenarios ([ticker](ticker.md), [retained](retained.md), [echo](echo.md),
[LWT](lwt.md)) and all QoS levels work identically over WebSocket.

## Sample Usage

### JavaScript (browser, MQTT.js)

```javascript
// MQTT.js in a browser connects over WebSocket.
const client = mqtt.connect("ws://localhost:9001");

client.on("connect", () => client.subscribe("apidash/test/#"));
client.on("message", (topic, payload) =>
  console.log(topic, payload.toString())
);
```
