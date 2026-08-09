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

## Why this is different from the other test endpoints (and why Docker)

**Before — HTTP / WebSocket / SSE:** every test endpoint is a FastAPI route
inside this app, served over its single HTTP(S) port. That works because HTTP,
WebSocket (an HTTP upgrade) and SSE all ride on HTTP — and Azure App Service
exposes exactly one HTTP/HTTPS port, which is all those need. No extra process,
no extra infra.

**MQTT is fundamentally different.** It's a stateful, connection-oriented
**pub/sub** protocol over its **own TCP ports** (1883 plaintext, 8883 TLS,
8083/8084 for MQTT-over-WebSocket), and it needs a **real broker** to hold
sessions, subscriptions, retained messages and QoS state. It is **not** HTTP, so:

- It **can't be a FastAPI route** like `/ws/echo` — there is no HTTP request to
  answer; the client keeps a long-lived MQTT connection open to a broker.
- Azure App Service **can't host a broker** either — it forwards only one
  HTTP/HTTPS port and cannot open raw TCP 1883/8883. (The WS endpoints work there
  *only* because WS is an HTTP upgrade over that same port.)
- Faking broker semantics (QoS 1/2 handshakes, retained, sessions, LWT, v5
  properties) as a FastAPI endpoint would mean re-implementing a broker, with
  poor fidelity — not worth it.

**So to test locally we run a real broker (Eclipse Mosquitto) + a publisher via
Docker** — one command, full fidelity, no cloud needed. That is the "extra
hassle": it buys you a spec-compliant broker to point the client at, instead of a
fake HTTP shim.

**What about production?** A shared, always-on hosted MQTT test endpoint (the
equivalent of `api.apidash.dev/ws/echo`) is a **separate, maintainer-owned
decision** — it needs a broker somewhere *outside* App Service (a managed broker
like HiveMQ/EMQX Cloud, or a self-hosted VM). **This change intentionally covers
local testing only;** the Azure/production infra is wired up separately.

## What this adds

- `mqtt/docker-compose.yml`, `mqtt/Dockerfile`, `mqtt/mosquitto/mosquitto.conf` —
  the Dockerized broker + publisher service.
- `mqtt/publisher.py` — the deterministic test-topic publisher (ticker, retained,
  echo request/response incl. v5 `response_topic`, Last Will).
- `docs/mqtt/` — this README plus per-scenario pages.
- `tests/mqtt/test_mqtt.py` — broker round-trip tests that skip when no broker is
  running (CI-safe).
- `paho-mqtt` added to `requirements-dev.txt` only — the production app
  (`requirements.txt`) is unchanged and pulls in no MQTT dependency.

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
