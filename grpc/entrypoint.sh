#!/bin/sh
# Entrypoint for API Dash's custom gRPC test server.
#
# Provisions the one thing the TLS listener (9001) needs on FIRST run -- a
# self-signed certificate -- so the whole rig comes up with a single
# `docker compose up` and no manual cert steps. The cert is created only if
# missing, so restarts reuse it. Mirrors the MQTT rig's broker entrypoint.
set -e

CERT_DIR="$(dirname "${GRPC_TLS_CERT:-/certs/server.crt}")"
CERT_FILE="${GRPC_TLS_CERT:-/certs/server.crt}"
KEY_FILE="${GRPC_TLS_KEY:-/certs/server.key}"

mkdir -p "$CERT_DIR"

# --- Self-signed TLS certificate (9001) ------------------------------------
if [ ! -f "$CERT_FILE" ]; then
  echo "[entrypoint] generating self-signed TLS certificate (CN=localhost) ..."
  # CN=localhost + a SAN for localhost/127.0.0.1 so hostname verification can
  # pass for clients that check it (API Dash's "allow invalid certs" is still
  # needed because the cert is self-signed / has no trusted CA).
  openssl req -x509 -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days 3650 -nodes \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
else
  echo "[entrypoint] reusing existing TLS certificate at $CERT_FILE"
fi

echo "[entrypoint] starting gRPC test server ..."
exec python server.py
