---
protocol: mqtt
title: MQTT Topic Wildcards
desc: Use the + (single level) and # (multi level) wildcards to subscribe across the apidash/test/ topic tree.
path: mqtt/wildcards
---

MQTT topics are hierarchical, using `/` as a separator (e.g.
`apidash/test/echo/response`). Subscriptions can use two wildcards. All test
topics live under the `apidash/test/` prefix, so wildcards are easy to try.

## Wildcards

| Wildcard | Meaning | Example subscription | Matches |
| ----------- | ----------- | ----------- | ----------- |
| `+` | Exactly one level | `apidash/test/echo/+` | `apidash/test/echo/request`, `apidash/test/echo/response` |
| `#` | Zero or more trailing levels | `apidash/test/#` | every topic under `apidash/test/` |

`+` matches a single level only: `apidash/test/+` matches `apidash/test/ticker`
but **not** `apidash/test/echo/response`. `#` must be the last character in the
filter.

## Try it

Subscribe to `apidash/test/#` to receive every test topic at once (ticker,
retained, echo responses, status). This is the quickest way to confirm the rig
is alive.

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.on_message = lambda cl, ud, msg: print(msg.topic, "->", msg.payload[:60])
c.connect("localhost", 1883)
c.subscribe("apidash/test/#", qos=0)
c.loop_forever()
# apidash/test/status -> b'online'
# apidash/test/retained -> b'{"note": ...}'
# apidash/test/ticker -> b'{"seq": 1, ...}'
```
