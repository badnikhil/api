# Custom gRPC test server image for API Dash's gRPC client.
#
# Serves apidash.test.TestService (see proto/apidash_test.proto) with mock/random
# data over both plaintext (9000) and TLS (9001). This replaces the old rig,
# which just ran the third-party moul/grpcbin image -- here we build and serve
# OUR OWN endpoints, the gRPC analogue of the MQTT rig's publisher image.
#
# Build context is the grpc/ directory (see docker-compose.yml).
FROM python:3.12-slim

WORKDIR /app

# openssl: used by entrypoint.sh to mint the self-signed cert for the TLS
# listener (9001) on first start.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openssl \
    && rm -rf /var/lib/apt/lists/*

# Install the gRPC libraries first (better layer caching). grpcio-tools is
# needed to generate the stubs during the build step below.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Proto + server, then generate the *_pb2.py / *_pb2_grpc.py stubs at build time
# so server.py can import them. Doing it here (not committing generated code)
# keeps the stubs in lockstep with the installed grpcio version.
COPY proto ./proto
RUN python -m grpc_tools.protoc \
    -I proto \
    --python_out=. \
    --grpc_python_out=. \
    proto/apidash_test.proto

COPY server.py ./
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Unbuffered stdout so `docker compose logs server` streams in real time.
ENV PYTHONUNBUFFERED=1

# Where the entrypoint writes / the server reads the self-signed TLS material.
ENV GRPC_TLS_CERT=/certs/server.crt \
    GRPC_TLS_KEY=/certs/server.key

EXPOSE 9000 9001

# The entrypoint generates the self-signed cert on first start (if missing),
# then execs the server.
ENTRYPOINT ["/entrypoint.sh"]
