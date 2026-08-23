---
protocol: grpc
title: gRPC Unary Call
desc: Single request, single response. Echo returns your message plus a server time and sequence number; GetRandomUser returns randomly generated mock data.
path: grpc/unary
---

A **unary** call is the simplest gRPC interaction: the client sends **one**
request message and the server returns **one** response message. It is the gRPC
analogue of a plain HTTP request/response and the first thing to try after
[reflection](reflection.md).

`apidash.test.TestService` exposes two unary methods:

- `Echo` -- echoes the `message` you send straight back, and adds the server's
  wall-clock time and a per-server **sequence number** that increments on every
  `Echo` call, so you can confirm the round-trip and see server-side state.
- `GetRandomUser` -- takes no input and returns a **randomly generated** `User`
  (mock data: a random name, email, age 18-80 and country) -- different on every
  call.

## What it tests

That API Dash can send a single Protobuf message and render the single response,
with all fields correctly encoded and decoded -- and that fields the server sets
itself (server time, sequence number, random data) come back populated.

## Methods

```
apidash.test.TestService/Echo            # EchoRequest{message} -> EchoResponse{message, server_time, seq}
apidash.test.TestService/GetRandomUser   # Empty -> User{id, name, email, age, country}
```

## Expected behavior

| Method | Request | Response |
| ----------- | ----------- | ----------- |
| `Echo` | `{"message": "hi"}` | `{"message": "hi", "server_time": "2026-...Z", "seq": N}` where `N` increments each call |
| `GetRandomUser` | `{}` (empty) | e.g. `{"id": "<uuid>", "name": "Ada Perlman", "email": "aperlman759@apidash.dev", "age": 46, "country": "Canada"}` -- random each time |

## Test it in API Dash

1. **Reflect** against `localhost:9000` and pick `apidash.test.TestService/Echo`.
2. Set the request to `{"message": "hello apidash"}` and **Send**.
   - **Expected:** the response echoes `message`, includes an ISO-8601
     `server_time`, and a `seq` (e.g. `1`). Send again -> `seq` becomes `2`.
3. Pick `GetRandomUser`, leave the request empty, and **Send** a few times.
   - **Expected:** a fully populated `User` each time, with a different
     `name`/`email`/`country` on repeated calls (the data is random).

## Sample Usage

### grpcurl

`Echo`:

```
grpcurl -plaintext -d '{"message": "hi"}' \
  localhost:9000 apidash.test.TestService/Echo
# {
#   "message": "hi",
#   "server_time": "2026-08-23T19:53:15.130694+00:00",
#   "seq": 1
# }
```

`GetRandomUser` (random mock data -- yours will differ):

```
grpcurl -plaintext -d '{}' \
  localhost:9000 apidash.test.TestService/GetRandomUser
# {
#   "id": "7d532bb8-...",
#   "name": "Ada Perlman",
#   "email": "aperlman759@apidash.dev",
#   "age": 46,
#   "country": "Canada"
# }
```

For the TLS listener use `localhost:9001` with `-insecure` (grpcurl) or TLS +
allow-invalid-certs (API Dash); see [tls](tls.md).
