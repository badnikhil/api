---
protocol: mqtt
title: MQTT Test Broker
desc: A one-command local Mosquitto broker plus a deterministic test publisher for exercising API Dash's MQTT client (QoS, retained, wildcards, LWT, MQTT v5).
path: mqtt
---

This is a **local** MQTT test rig for API Dash's MQTT client. MQTT is not an
HTTP route, so unlike the WebSocket endpoints it cannot be hosted inside the
FastAPI app. Instead we ship a Dockerized [Eclipse Mosquitto](https://mosquitto.org/)
2.x broker plus a small `paho-mqtt` publisher that generates deterministic,
subscribable traffic -- the MQTT analogue of the WebSocket echo / ticker /
heartbeat routes.

Running a real, spec-compliant broker is the only way to genuinely test QoS 1/2
handshakes, retained messages, persistent sessions, Last Will and MQTT v5
properties.

## Run it

From the repository root:

```
docker compose -f mqtt/docker-compose.yml up
```

This starts two services:

| Service | What it is |
| ----------- | ----------- |
| `broker` | Eclipse Mosquitto 2.x (MQTT v3.1 / v3.1.1 / v5) |
| `publisher` | A `paho-mqtt` client that emits the test scenarios below |

Stop it with `Ctrl-C`, or run detached with `-d` and stop via
`docker compose -f mqtt/docker-compose.yml down`.

## Endpoints

| Transport | URL |
| ----------- | ----------- |
| MQTT over TCP | `mqtt://localhost:1883` |
| MQTT over WebSocket | `ws://localhost:9001` |

Anonymous access is allowed by default (no username/password needed). See
[Auth](auth.md) to test username/password.

## Point API Dash at it

In API Dash's MQTT client, create a connection to:

- **Host:** `localhost`
- **Port:** `1883` (TCP) or `9001` (WebSocket)
- **Protocol:** MQTT v3.1.1 or v5 (both work)
- **Auth:** none (anonymous), unless you enabled it

Then subscribe to `apidash/test/#` to see every test topic at once.

## Test topics

| Topic | Scenario | Doc |
| ----------- | ----------- | ----------- |
| `apidash/test/ticker` | JSON message every 2s (QoS 0) | [ticker](ticker.md) |
| `apidash/test/retained` | Retained message, delivered on subscribe | [retained](retained.md) |
| `apidash/test/echo/request` -> `apidash/test/echo/response` | Request/response echo | [echo](echo.md) |
| `apidash/test/status` | `online` / `offline` via Last Will (retained) | [lwt](lwt.md) |

Further reference pages: [wildcards](wildcards.md), [qos](qos.md),
[auth](auth.md), [MQTT v5 properties](v5_properties.md),
[WebSocket transport](websocket.md).

## Tests

`tests/mqtt/test_mqtt.py` exercises the broker with `paho-mqtt`. The tests skip
gracefully if no broker is reachable, so CI without a broker still passes:

```
docker compose -f mqtt/docker-compose.yml up -d
pip install -r requirements-dev.txt
pytest tests/mqtt/test_mqtt.py
```
