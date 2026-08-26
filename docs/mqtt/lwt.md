---
protocol: mqtt
title: MQTT Last Will (LWT)
desc: The publisher registers a Last Will on apidash/test/status; killing it makes the broker publish "offline" automatically.
path: mqtt/lwt
---

A **Last Will and Testament (LWT)** is a message the client registers at connect
time; the broker publishes it automatically if the client disconnects
**ungracefully** (crash, network drop, kill). It is how MQTT signals presence.

The publisher registers a Will on `apidash/test/status` with payload `offline`
(retained), and publishes `online` (retained) once connected.

## Topic

```
apidash/test/status
```

## Behavior

| Event | Value on `apidash/test/status` |
| ----------- | ----------- |
| Publisher connected | `online` (retained) |
| Publisher killed / crashes / loses connection | `offline` (retained, published by the broker as the Will) |

Because the value is retained, a client that subscribes at any time
immediately sees the current status.

## Try it

1. Subscribe to `apidash/test/status` -- you see `online`.
2. Ungracefully stop the publisher so it cannot send a clean disconnect:

   ```
   docker compose -f mqtt/docker-compose.yml kill publisher
   ```

3. The broker publishes the Will -- you now see `offline`.

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.on_message = lambda cl, ud, msg: print("status:", msg.payload.decode())
c.connect("localhost", 1883)
c.subscribe("apidash/test/status", qos=1)
c.loop_forever()
# status: online
# (after `docker compose -f mqtt/docker-compose.yml kill publisher`)
# status: offline
```
