#!/usr/bin/env python3
"""
Deterministic MQTT test publisher for API Dash's MQTT client.

This is the MQTT analogue of the WebSocket echo / ticker / heartbeat test
routes (see docs/ws/*). It connects to a real Mosquitto broker and produces
predictable, subscribable traffic so an MQTT client (such as API Dash) can be
exercised end to end -- QoS, retained messages, wildcards, Last Will and
MQTT v5 request/response properties.

Scenarios (every topic lives under the `apidash/test/` prefix):

  ticker    -> publishes JSON {"seq": n, "ts": <iso8601>} to
               apidash/test/ticker every 2s (QoS 0).
  retained  -> publishes a RETAINED message to apidash/test/retained at
               startup, so a client that subscribes LATER still receives it
               immediately.
  echo      -> subscribes apidash/test/echo/request; each message received is
               republished to apidash/test/echo/response. If the incoming
               MQTT v5 PUBLISH carries a `response_topic` property, the reply
               is sent there instead, echoing back any `correlation_data`.
  lwt       -> registers a Last Will on apidash/test/status = "offline"
               (retained), and publishes "online" (retained) on connect.
               Kill this process ungracefully (e.g.
               `docker compose -f mqtt/docker-compose.yml kill publisher`)
               to watch the broker deliver the Will.

Configuration (environment variables):
  MQTT_HOST        broker hostname            (default: localhost)
  MQTT_PORT        broker TCP port            (default: 1883)
  MQTT_USER        username, optional
  MQTT_PASS        password, optional
  MQTT_CLIENT_ID   client id                  (default: apidash-test-publisher)

Everything here is intentionally simple and heavily commented -- it is a
testing fixture, not production code.
"""

import json
import os
import signal
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

# --- Topic names (single source of truth; mirrored in docs/mqtt/*.md) --------
TOPIC_PREFIX = "apidash/test"
TICKER_TOPIC = f"{TOPIC_PREFIX}/ticker"
RETAINED_TOPIC = f"{TOPIC_PREFIX}/retained"
ECHO_REQUEST_TOPIC = f"{TOPIC_PREFIX}/echo/request"
ECHO_RESPONSE_TOPIC = f"{TOPIC_PREFIX}/echo/response"
STATUS_TOPIC = f"{TOPIC_PREFIX}/status"

TICKER_INTERVAL_SECONDS = 2

# --- Configuration from the environment -------------------------------------
MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USER")
MQTT_PASS = os.environ.get("MQTT_PASS")
CLIENT_ID = os.environ.get("MQTT_CLIENT_ID", "apidash-test-publisher")


def log(msg):
    """Timestamped stdout logging (see `docker compose logs publisher`)."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] {msg}", flush=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def build_client():
    """Create an MQTT v5 client using the modern (v2) callback API when
    available, falling back to the paho-mqtt 1.x constructor otherwise."""
    try:
        return mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=CLIENT_ID,
            protocol=mqtt.MQTTv5,
        )
    except AttributeError:
        # paho-mqtt 1.x has no CallbackAPIVersion enum.
        return mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv5)


# --- Callbacks --------------------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    """Runs on every (re)connect -- so it is safe to re-publish + re-subscribe."""
    log(f"connected to {MQTT_HOST}:{MQTT_PORT} (reason_code={reason_code})")

    # LWT counterpart: announce we are online (retained). A late subscriber to
    # apidash/test/status sees "online" until we disconnect ungracefully.
    client.publish(STATUS_TOPIC, payload="online", qos=1, retain=True)
    log(f"published retained '{STATUS_TOPIC}' = 'online'")

    # Retained scenario: any FUTURE subscriber gets this immediately.
    retained_payload = json.dumps(
        {
            "note": (
                "This is a retained message. A client that subscribes AFTER "
                "it was published still receives it immediately on subscribe."
            ),
            "ts": now_iso(),
        }
    )
    client.publish(RETAINED_TOPIC, payload=retained_payload, qos=1, retain=True)
    log(f"published retained '{RETAINED_TOPIC}'")

    # Echo scenario: listen for requests (QoS 1 so the broker can redeliver).
    client.subscribe(ECHO_REQUEST_TOPIC, qos=1)
    log(f"subscribed '{ECHO_REQUEST_TOPIC}' (qos=1)")


def on_disconnect(client, userdata, *args):
    # Signature differs across paho versions, so accept whatever is passed.
    log(f"disconnected {args}; paho will auto-reconnect")


def on_message(client, userdata, msg):
    """Echo handler: mirror each request onto the response topic."""
    payload = msg.payload
    log(f"echo request on '{msg.topic}' ({len(payload)} bytes)")

    # MQTT v5 request/response: honour `response_topic` + `correlation_data`.
    response_topic = ECHO_RESPONSE_TOPIC
    reply_props = None
    incoming = getattr(msg, "properties", None)
    if incoming is not None:
        response_topic = getattr(incoming, "ResponseTopic", None) or ECHO_RESPONSE_TOPIC
        correlation = getattr(incoming, "CorrelationData", None)
        if correlation is not None:
            reply_props = Properties(PacketTypes.PUBLISH)
            reply_props.CorrelationData = correlation

    client.publish(response_topic, payload=payload, qos=1, properties=reply_props)
    log(f"echo reply -> '{response_topic}'")


# --- Ticker thread ----------------------------------------------------------
def ticker_loop(client, stop_event):
    seq = 0
    while not stop_event.is_set():
        seq += 1
        payload = json.dumps({"seq": seq, "ts": now_iso()})
        # QoS 0 -- fire and forget, like the WebSocket ticker route.
        client.publish(TICKER_TOPIC, payload=payload, qos=0)
        log(f"ticker -> '{TICKER_TOPIC}' seq={seq}")
        stop_event.wait(TICKER_INTERVAL_SECONDS)


def main():
    client = build_client()

    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    # Last Will and Testament: if we drop off ungracefully, the broker
    # publishes this retained message on our behalf.
    client.will_set(STATUS_TOPIC, payload="offline", qos=1, retain=True)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Robust reconnect: paho retries with exponential backoff between these
    # bounds after any unexpected disconnect.
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    # The broker may not be ready yet (docker compose starts it in parallel),
    # so retry the INITIAL connect until it succeeds.
    while True:
        try:
            log(f"connecting to {MQTT_HOST}:{MQTT_PORT} ...")
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
            break
        except Exception as exc:  # noqa: BLE001 - test fixture: log and retry
            log(f"connect failed: {exc!r}; retrying in 2s")
            time.sleep(2)

    stop_event = threading.Event()

    def handle_signal(signum, frame):
        # NOTE: we deliberately do NOT send a clean DISCONNECT here. Exiting
        # without a DISCONNECT packet makes the broker fire the Last Will, so
        # stopping/killing this container demonstrates LWT on apidash/test/status.
        log(f"signal {signum} received; stopping (Will fires on ungraceful close)")
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # Network loop runs in the background; the ticker runs on its own thread.
    stop_event_thread = threading.Thread(
        target=ticker_loop, args=(client, stop_event), daemon=True
    )
    client.loop_start()
    stop_event_thread.start()

    # Block the main thread until we are told to stop.
    while not stop_event.is_set():
        time.sleep(0.5)

    stop_event_thread.join(timeout=5)
    client.loop_stop()  # stop the network thread WITHOUT sending DISCONNECT
    log("stopped")


if __name__ == "__main__":
    main()
