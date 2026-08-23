---
protocol: grpc
title: gRPC over TLS
desc: The test server serves the same apidash.test.TestService over TLS on port 9001 with a self-signed certificate -- point API Dash there with TLS on and allow invalid certificates.
path: grpc/tls
---

The test server serves gRPC **over TLS** on port `9001`, so you can exercise API
Dash's encrypted-transport support. It is the **same service and methods** as the
plaintext `9000` listener -- only the transport differs: `9001` speaks gRPC over
HTTP/2 with TLS, while `9000` is cleartext HTTP/2 (h2c).

The certificate is **self-signed** (no trusted CA), so clients must be told to
accept it -- the gRPC analogue of the MQTT rig's TLS listener and its
"Allow Invalid Certificates". The Docker entrypoint mints this cert
(`CN=localhost`, with a `localhost`/`127.0.0.1` SAN) on first start.

## What it tests

That API Dash can establish a TLS-secured gRPC channel and run every call type
(reflection, unary, streaming, metadata, errors) over it -- and that its
"allow invalid certificates" toggle works against a self-signed server.

## Endpoint

```
localhost:9001   # gRPC over TLS (h2), self-signed cert
```

The plaintext equivalent is `localhost:9000`; see the [overview](README.md).

## Point API Dash at it

In API Dash's gRPC client, create a request to:

- **Server / address:** `localhost:9001`
- **TLS / Use TLS:** **on**
- **Allow Invalid Certificates:** **on** (the cert is self-signed with no
  trusted CA, so certificate validation must be relaxed)

Then hit **Reflect** and use any method exactly as on `9000`.

## Expected behavior

| Setting | Result |
| ----------- | ----------- |
| TLS on + Allow Invalid Certificates on | Connection succeeds (encrypted) |
| TLS on + strict validation | Fails -- the self-signed cert has no trusted CA |
| TLS off (plaintext to `9001`) | Fails -- the listener only speaks TLS |
| TLS on to `9000` | Fails -- `9000` is plaintext h2c, not TLS |

## Test it in API Dash

1. Create a request to `localhost:9001` with **TLS on** and **Allow Invalid
   Certificates on**.
2. Hit **Reflect** -- **Expected:** the same `apidash.test.TestService` with its
   seven methods appears, exactly as on `9000`.
3. Run any method (e.g. `Echo` with `{"message": "over tls"}`) -- **Expected:**
   it succeeds over the encrypted channel.
4. As a negative check, turn **Allow Invalid Certificates off** -- **Expected:**
   the connection now fails (the self-signed cert isn't trusted).

## Sample Usage

### grpcurl

For the TLS listener, drop `-plaintext` and add `-insecure` (skip certificate
verification -- the grpcurl equivalent of "Allow Invalid Certificates"):

```
grpcurl -insecure localhost:9001 list
# apidash.test.TestService
# grpc.reflection.v1alpha.ServerReflection
```

```
grpcurl -insecure -d '{"message": "over tls"}' \
  localhost:9001 apidash.test.TestService/Echo
# {
#   "message": "over tls",
#   "server_time": "...",
#   "seq": 1
# }
```

Every method documented for `9000` -- [reflection](reflection.md),
[unary](unary.md), [server_streaming](server_streaming.md),
[client_streaming](client_streaming.md), [bidi](bidi.md),
[metadata](metadata.md), [errors](errors.md) -- works identically on `9001`;
just swap `-plaintext` for `-insecure` and the port to `9001`. For a real
CA-signed server you would drop `-insecure` and pass `-cacert <ca.pem>` instead.
