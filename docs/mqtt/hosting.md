---
protocol: mqtt
title: Hosting a Public MQTT Test Broker
desc: Maintainer notes for standing up a shared, always-on MQTT broker (with TLS + auth) outside Azure App Service, so contributors need zero local setup.
path: mqtt/hosting
---

The Docker rig in this folder is for **local** testing. This page is a short set
of **maintainer notes** for the separate decision of hosting a **public,
always-on** broker -- the equivalent of `api.apidash.dev/ws/echo` for MQTT -- so
contributors can point API Dash at a hostname with **zero local setup**.

## Why not Azure App Service

The HTTP/WS/SSE test endpoints live in the FastAPI app on Azure App Service
because they all ride on **one HTTP/HTTPS port**. MQTT is a stateful pub/sub
protocol on its **own raw TCP ports** (`1883`/`8883`, plus `9001`/`8083`/`8084`
for MQTT-over-WebSocket). App Service forwards only a single HTTP port and
cannot open raw TCP, so **it cannot host a broker.** A broker has to live
somewhere else.

## Option A -- Managed broker (least maintenance)

Use a hosted MQTT service and just hand out the connection details:

- **HiveMQ Cloud** or **EMQX Cloud** -- both have a free serverless tier, give
  you a stable TLS hostname (`xxxxx.s1.eu.hivemq.cloud:8883`), and manage certs
  and uptime for you.
- Create a test user (e.g. `testuser` / `testpass`), publish the host + port +
  credentials, and you are done. No servers to patch.

This is the lowest-effort "always-on" option and is recommended unless there is
a reason to self-host.

## Option B -- Self-hosted VM (this same image)

Run the exact Mosquitto image from this rig on a small VM (any cloud's cheapest
instance, or a container host that can expose raw TCP):

1. Deploy `mqtt/mosquitto/` (the Dockerfile + config) to the VM.
2. Put it behind a **stable hostname** with **real TLS** -- replace the
   self-signed cert with a CA-signed one (Let's Encrypt via DNS-01, since MQTT
   ports are not HTTP), so clients don't need "Allow Invalid Certificates".
3. Keep the **auth listener** so the public endpoint isn't an open relay; hand
   out `testuser` / `testpass` (or per-scenario creds).
4. Open the broker's TCP ports (`8883` for TLS, optionally `8084` for secure
   WebSocket) in the VM firewall.

Note the container-host caveat: platforms that only expose HTTP (App Service,
some PaaS) won't work -- you need one that can publish arbitrary TCP ports (a
plain VM, or a Kubernetes `LoadBalancer`/`NodePort` service).

## Recommendation

For a public API Dash test broker, start with a **managed broker (Option A)**:
it is always-on, TLS + auth out of the box, and needs no patching. Fall back to
the **self-hosted VM (Option B)** only if you want full control or to avoid a
third-party dependency. Either way this is a maintainer-owned decision and is
intentionally **out of scope** for the local rig.
