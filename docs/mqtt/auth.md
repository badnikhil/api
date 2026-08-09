---
protocol: mqtt
title: MQTT Username/Password Auth
desc: Anonymous by default for frictionless testing; optionally enable a password file to test username/password authentication.
path: mqtt/auth
---

By default the broker allows **anonymous** connections so local testing is
frictionless (`allow_anonymous true` in `mqtt/mosquitto/mosquitto.conf`). You
can switch on username/password auth to test API Dash's credential handling.

## Enable auth

1. Create a password file inside the broker container:

   ```
   docker compose -f mqtt/docker-compose.yml exec broker \
     mosquitto_passwd -c -b /mosquitto/config/passwd testuser testpass
   ```

2. In `mqtt/mosquitto/mosquitto.conf`, uncomment the `password_file` line and
   set `allow_anonymous false` (a commented-out template block is already
   there).

3. Recreate the broker:

   ```
   docker compose -f mqtt/docker-compose.yml up -d --force-recreate broker
   ```

The publisher itself reads optional `MQTT_USER` / `MQTT_PASS` env vars, so set
those in `docker-compose.yml` if you enable auth and want the publisher to keep
working.

## Behavior

| Credentials | Result |
| ----------- | ----------- |
| `allow_anonymous true` (default) | Any client may connect without credentials |
| `allow_anonymous false` + valid `testuser` / `testpass` | Connection accepted |
| `allow_anonymous false` + missing/wrong credentials | Broker refuses the connection (CONNACK "not authorized") |

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.username_pw_set("testuser", "testpass")
c.connect("localhost", 1883)
c.loop_forever()
```
