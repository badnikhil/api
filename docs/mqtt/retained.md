---
protocol: mqtt
title: MQTT Retained Message
desc: The publisher stores a retained message on apidash/test/retained so any client that subscribes later receives it immediately.
path: mqtt/retained
---

At startup (and on every reconnect) the publisher stores a **retained** message
on `apidash/test/retained`. The broker keeps the last retained message for a
topic and delivers it immediately to any client that subscribes **later** -- a
core MQTT feature that has no WebSocket equivalent.

## Topic

```
apidash/test/retained
```

## Behavior

| Event | Result |
| ----------- | ----------- |
| Subscribe (any time) | You immediately receive the retained JSON payload, with the retain flag set |
| Publisher restarts | The retained message is refreshed with a new timestamp |

The payload is a JSON object with a `note` and a `ts` (ISO-8601) field.

To clear a retained message on any topic, publish an **empty** payload to it
with the retain flag set.

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.on_message = lambda cl, ud, msg: print("retain=%s" % msg.retain, msg.payload.decode())
c.connect("localhost", 1883)
# Even though this runs long after the publisher started, the message arrives
# immediately on subscribe.
c.subscribe("apidash/test/retained", qos=1)
c.loop_forever()
# retain=True {"note": "This is a retained message. ...", "ts": "..."}
```
