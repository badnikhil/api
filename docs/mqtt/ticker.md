---
protocol: mqtt
title: MQTT Ticker
desc: The publisher emits a JSON ticker message to apidash/test/ticker every 2 seconds at QoS 0.
path: mqtt/ticker
---

The test publisher emits a JSON message to `apidash/test/ticker` every **2
seconds** at **QoS 0**. It is the MQTT analogue of the WebSocket ticker route
and is intended for testing server-push / streaming handling in an MQTT client
such as API Dash.

## Topic

```
apidash/test/ticker
```

## Behavior

| Event | Result |
| ----------- | ----------- |
| Every 2s | Publisher sends `{"seq": <n>, "ts": "<iso8601>"}` at QoS 0 |
| Subscribe | You start receiving ticks from the next interval onward |

`seq` starts at `1` and increments for the lifetime of the publisher process.
Because this topic is **not** retained, a new subscriber only sees ticks
published after it subscribes.

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.on_message = lambda cl, ud, msg: print(msg.topic, msg.payload.decode())
c.connect("localhost", 1883)
c.subscribe("apidash/test/ticker", qos=0)
c.loop_forever()
# apidash/test/ticker {"seq": 1, "ts": "..."}
# apidash/test/ticker {"seq": 2, "ts": "..."}
```
