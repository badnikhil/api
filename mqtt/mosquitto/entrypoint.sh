#!/bin/sh
# Broker entrypoint for API Dash's local MQTT test rig.
#
# Provisions everything the config needs on FIRST run so the whole rig comes up
# with a single `docker compose up` -- no manual cert/password steps:
#
#   * a self-signed TLS certificate (for the 8883 TLS listener), and
#   * a username/password file pre-seeded with testuser / testpass
#     (for the 1884 auth listener).
#
# Both are created only if missing, so restarts reuse the existing secrets.
# The mosquitto.conf is mounted read-only, so secrets are written to writable
# locations: certs to /mosquitto/certs, the password file to /mosquitto/config.
set -e

CERT_DIR=/mosquitto/certs
PASSWD_FILE=/mosquitto/config/passwd

mkdir -p "$CERT_DIR"

# --- Self-signed TLS certificate (8883) ------------------------------------
if [ ! -f "$CERT_DIR/server.crt" ]; then
  echo "[entrypoint] generating self-signed TLS certificate (CN=localhost) ..."
  openssl req -x509 -newkey rsa:2048 \
    -keyout "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.crt" \
    -days 3650 -nodes -subj "/CN=localhost"
else
  echo "[entrypoint] reusing existing TLS certificate in $CERT_DIR"
fi

# --- Username/password file (1884) -----------------------------------------
if [ ! -f "$PASSWD_FILE" ]; then
  echo "[entrypoint] seeding password file with testuser/testpass ..."
  mosquitto_passwd -c -b "$PASSWD_FILE" testuser testpass
else
  echo "[entrypoint] reusing existing password file $PASSWD_FILE"
fi

# mosquitto starts as root here and drops privileges to the 'mosquitto' user,
# so make the generated secrets owned by (and readable only by) that user.
chown -R mosquitto:mosquitto "$CERT_DIR" "$PASSWD_FILE" 2>/dev/null || true
chmod 600 "$CERT_DIR/server.key" "$PASSWD_FILE" 2>/dev/null || true

echo "[entrypoint] starting mosquitto ..."
exec mosquitto -c /mosquitto/config/mosquitto.conf
