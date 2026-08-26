---
protocol: mqtt
title: MQTT Username/Password Auth
desc: An always-on auth listener on port 1884 (testuser/testpass) needs no config edits; the main 1883 listener stays anonymous, and you can optionally require auth there too.
path: mqtt/auth
---

The rig exposes a **dedicated, always-on auth listener on port `1884`** so you
can test API Dash's username/password handling with **zero setup** -- no config
edits, no container commands. It is pre-seeded with `testuser` / `testpass`,
generated automatically by the broker on first start.

The main `1883` listener stays **anonymous** so everyday testing is still
frictionless. Both listeners talk to the same broker and share all topics.

## The easy path: connect to port 1884

Point API Dash at:

- **Host:** `localhost`
- **Port:** `1884`
- **Username:** `testuser`
- **Password:** `testpass`

Anonymous connects to `1884` are refused, so it also lets you verify how API
Dash surfaces a rejected ("not authorized") connection: connect with no
credentials, or the wrong password, and the broker denies it.

## Behavior

| Listener | Credentials | Result |
| ----------- | ----------- | ----------- |
| `1883` (anonymous) | none | Connection accepted |
| `1884` (auth)      | valid `testuser` / `testpass` | Connection accepted |
| `1884` (auth)      | missing or wrong credentials | Broker refuses the connection (CONNACK "not authorized") |

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
c.username_pw_set("testuser", "testpass")
c.connect("localhost", 1884)   # the auth listener
c.loop_forever()
```

## Alternative: require auth on the main port (1883)

If you'd rather require credentials on the primary `1883` listener instead of
using the dedicated `1884` one, edit the `listener 1883` block in
`mqtt/mosquitto/mosquitto.conf` to:

```
listener 1883
protocol mqtt
allow_anonymous false
password_file /mosquitto/config/passwd
```

The password file (`testuser` / `testpass`) is already created by the broker
entrypoint, so you only change the config and restart:

```
docker compose -f mqtt/docker-compose.yml up -d --force-recreate broker
```

To add more users, exec into the broker and append to the same file:

```
docker compose -f mqtt/docker-compose.yml exec broker \
  mosquitto_passwd -b /mosquitto/config/passwd anotheruser anotherpass
```

then restart the broker. The publisher itself reads optional `MQTT_USER` /
`MQTT_PASS` env vars, so set those in `docker-compose.yml` if you require auth on
`1883` and want the publisher to keep working.
