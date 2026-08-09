---
protocol: mqtt
title: MQTT Quality of Service (QoS)
desc: Test QoS 0, 1 and 2 delivery guarantees against the broker; the effective QoS is the minimum of the publish and subscribe QoS.
path: mqtt/qos
---

MQTT defines three Quality of Service (QoS) levels for message delivery. A real
broker is required to exercise the QoS 1 and QoS 2 handshakes, which is one of
the main reasons this rig ships a Dockerized Mosquitto.

## Levels

| QoS | Guarantee | Handshake |
| ----------- | ----------- | ----------- |
| 0 | At most once ("fire and forget") | none |
| 1 | At least once (may duplicate) | PUBLISH / PUBACK |
| 2 | Exactly once | PUBLISH / PUBREC / PUBREL / PUBCOMP |

The QoS a subscriber actually receives is the **minimum** of the publisher's
QoS and the subscription's QoS. For example, a QoS 2 publish delivered to a QoS
1 subscription is received at QoS 1.

## Try it with the test topics

- The [ticker](ticker.md) publishes at **QoS 0** -- subscribe at any QoS.
- The [echo](echo.md) and [retained](retained.md) topics use **QoS 1**.
- To exercise **QoS 2**, publish to your own topic (e.g.
  `apidash/test/scratch`) at QoS 2 and subscribe at QoS 2.

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.on_message = lambda cl, ud, msg: print("qos", msg.qos, msg.payload.decode())
c.connect("localhost", 1883)
c.subscribe("apidash/test/scratch", qos=2)
c.loop_start()

info = c.publish("apidash/test/scratch", payload="exactly once", qos=2)
info.wait_for_publish(5)  # completes only after the full QoS 2 handshake
# qos 2 exactly once
```
