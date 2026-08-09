---
protocol: mqtt
title: MQTT Echo
desc: Publish to apidash/test/echo/request and the publisher mirrors the payload back on apidash/test/echo/response (honouring the MQTT v5 response topic if present).
path: mqtt/echo
---

The publisher subscribes to `apidash/test/echo/request`. Every message it
receives is republished unchanged to `apidash/test/echo/response`. This is the
MQTT analogue of the WebSocket echo route and is useful for testing a full
publish -> subscribe round-trip.

If the incoming PUBLISH carries an **MQTT v5 `response_topic` property**, the
reply is sent there instead, and any `correlation_data` is echoed back. See
[MQTT v5 properties](v5_properties.md).

## Topics

| Topic | Direction |
| ----------- | ----------- |
| `apidash/test/echo/request` | You publish here |
| `apidash/test/echo/response` | Publisher replies here (default) |

## Behavior

| Event | Result |
| ----------- | ----------- |
| Publish to `.../echo/request` | Payload is republished to `.../echo/response`, unchanged |
| Request carries v5 `response_topic` | Reply is sent to that topic instead |
| Request carries v5 `correlation_data` | The same `correlation_data` is set on the reply |

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.on_message = lambda cl, ud, msg: print("reply:", msg.payload.decode())
c.connect("localhost", 1883)
c.subscribe("apidash/test/echo/response", qos=1)
c.loop_start()

c.publish("apidash/test/echo/request", payload="ping", qos=1)
# reply: ping
```
