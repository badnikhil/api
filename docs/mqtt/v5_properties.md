---
protocol: mqtt
title: MQTT v5 Properties
desc: The broker and echo scenario support MQTT v5 features such as response topic and correlation data for request/response messaging.
path: mqtt/v5_properties
---

Mosquitto 2.x supports **MQTT v5** with no extra configuration, so you can test
API Dash's v5 features against this rig. Connect with the v5 protocol
(`protocol=mqtt.MQTTv5` in paho).

## Request/response (echo)

The [echo](echo.md) scenario demonstrates the v5 request/response pattern:

| Property | Behavior |
| ----------- | ----------- |
| `response_topic` | If a request to `apidash/test/echo/request` sets a response topic, the publisher sends the reply there instead of `apidash/test/echo/response`. |
| `correlation_data` | If present on the request, the same bytes are set on the reply, so you can match responses to requests. |

## Other v5 features you can test against the broker

- **User properties** -- arbitrary key/value metadata on a PUBLISH.
- **Message expiry interval** -- retained/queued messages that auto-expire.
- **Session expiry interval** -- how long the broker keeps session state after
  disconnect.
- **Content type / payload format indicator**.

These are broker-level features; publish/subscribe with the properties set and
observe them on the receiving side.

## Sample Usage

### Python (`paho-mqtt`), request/response

```python
import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.on_message = lambda cl, ud, msg: print(
    "reply:", msg.payload.decode(),
    "correlation:", getattr(msg.properties, "CorrelationData", None),
)
c.connect("localhost", 1883)
c.subscribe("apidash/test/reply", qos=1)
c.loop_start()

props = Properties(PacketTypes.PUBLISH)
props.ResponseTopic = "apidash/test/reply"
props.CorrelationData = b"req-42"
c.publish("apidash/test/echo/request", payload="ping", qos=1, properties=props)
# reply: ping correlation: b'req-42'
```
