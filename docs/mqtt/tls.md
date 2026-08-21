---
protocol: mqtt
title: MQTT over TLS
desc: An encrypted MQTT listener on port 8883 using a self-signed certificate generated automatically on first start -- no manual cert setup.
path: mqtt/tls
---

The broker exposes **MQTT over TLS** on port `8883`, so you can exercise API
Dash's encrypted-transport support. The certificate is **self-signed and
generated automatically** by the broker on first start -- there are no manual
`openssl` steps.

Because the certificate is self-signed (CN `localhost`, no trusted CA), clients
must be told to accept it. `require_certificate false` means the broker does
**not** ask the client for a certificate -- this is server-side encryption only,
not mutual TLS.

## Endpoint

```
mqtts://localhost:8883
```

The other listeners are unencrypted: `mqtt://localhost:1883` (TCP),
`ws://localhost:9001` (WebSocket), `mqtt://localhost:1884` (auth). See the
[overview](README.md).

## Point API Dash at it

In API Dash's MQTT client, create a connection to:

- **Host:** `localhost`
- **Port:** `8883`
- **Use TLS:** **on**
- **Allow Invalid Certificates:** **on** (the cert is self-signed with no
  trusted CA, so certificate validation must be relaxed)

## Behavior

| Setting | Result |
| ----------- | ----------- |
| Use TLS on + Allow Invalid Certificates on | Connection succeeds (encrypted) |
| Use TLS on + strict validation | Fails -- the self-signed cert has no trusted CA |
| Use TLS off (plaintext to `8883`) | Fails -- the listener only speaks TLS |

## Sample Usage

### Python (`paho-mqtt`)

```python
import paho.mqtt.client as mqtt

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
# Encrypt the connection but accept the self-signed cert (the paho equivalent
# of "Allow Invalid Certificates"). For a real CA-signed broker, drop
# tls_insecure_set and pass ca_certs=<your CA> to tls_set instead.
c.tls_set()               # use the system CA store / default TLS settings
c.tls_insecure_set(True)  # do not verify the server hostname / self-signed cert
c.connect("localhost", 8883)
c.loop_forever()
```

### Command line (`mosquitto_pub` / `mosquitto_sub`)

The broker writes its cert to a named Docker volume. To test from the host with
the CA file, first copy the cert out of the container:

```
docker compose -f mqtt/docker-compose.yml exec broker \
  cat /mosquitto/certs/server.crt > server.crt

mosquitto_sub -h localhost -p 8883 --cafile server.crt --insecure \
  -t 'apidash/test/#'
```

`--insecure` skips hostname verification (the self-signed cert's CN is
`localhost`), mirroring "Allow Invalid Certificates".
