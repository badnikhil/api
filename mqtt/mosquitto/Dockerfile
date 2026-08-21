# Broker image for API Dash's local MQTT test rig.
#
# Based on the official Eclipse Mosquitto 2.x image, this adds `openssl` so the
# broker can generate a self-signed TLS certificate on first start, and an
# entrypoint that pre-seeds both the TLS cert and the username/password file
# before launching mosquitto. `mosquitto_passwd` already ships in the base image.
#
# Everything is provisioned automatically at container start -- there are no
# manual setup steps beyond `docker compose up`.
FROM eclipse-mosquitto:2

# openssl: used by entrypoint.sh to mint the self-signed cert for the TLS
# listener (8883). mosquitto_passwd (for the auth listener) is already present.
RUN apk add --no-cache openssl

# Entrypoint generates secrets on first run, then execs mosquitto.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
