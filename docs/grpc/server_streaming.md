---
protocol: grpc
title: gRPC Server Streaming
desc: One request, a stream of responses. StreamTicks streams N random-valued ticks (a price/sensor-style feed) at your chosen interval.
path: grpc/server_streaming
---

In a **server-streaming** call the client sends **one** request and the server
returns a **stream** of response messages, ending with a status. It is the gRPC
analogue of the WebSocket ticker route -- a single ask, many pushes.

`apidash.test.TestService` exposes one server-streaming method:

- `StreamTicks` -- streams back `count` `Tick` messages, one every
  `interval_ms` milliseconds. Each `Tick` carries a 1-based `seq`, a **random**
  `value` (a "price"/"reading" between 0 and 100), and a server `ts` timestamp,
  like a price or sensor feed.

Both request fields have **sane defaults** when left at 0: `count` defaults to
**10**, `interval_ms` to **500**. `count` is capped (default max 1000) and
`interval_ms` is capped at 10s so a single request can't run away.

## What it tests

That API Dash opens the stream, renders each message as it arrives, and closes
cleanly on the final status -- rather than waiting for a single response.

## Method

```
apidash.test.TestService/StreamTicks    # TickRequest{count, interval_ms} -> stream of Tick{seq, value, ts}
```

## Expected behavior

| Request | Response |
| ----------- | ----------- |
| `{"count": 5, "interval_ms": 200}` | 5 `Tick`s with `seq` 1..5, random `value`, ~200ms apart, then a final `OK` status |
| `{}` (both 0) | 10 `Tick`s, 500ms apart (the defaults), then `OK` |
| `{"count": 100000}` | Capped to the server maximum (default 1000) ticks |

Each streamed message arrives as a separate frame; the call completes when the
server sends the trailing status.

## Test it in API Dash

1. **Reflect** against `localhost:9000` and pick
   `apidash.test.TestService/StreamTicks`.
2. Set the request to `{"count": 5, "interval_ms": 500}` and **Send**.
   - **Expected:** five messages appear one at a time (~half a second apart),
     each with an incrementing `seq` (1..5), a different random `value`, and a
     `ts`; the stream then ends with an `OK` status.
3. Try `{}` (empty) to see the defaults: **10** ticks, 500ms apart.

## Sample Usage

### grpcurl

grpcurl prints each streamed message as it arrives:

```
grpcurl -plaintext -d '{"count": 5, "interval_ms": 200}' \
  localhost:9000 apidash.test.TestService/StreamTicks
# {"seq": 1, "value": 25.5768, "ts": "2026-08-23T19:53:15.132564+00:00"}
# {"seq": 2, "value": 18.6069, "ts": "2026-08-23T19:53:15.182776+00:00"}
# {"seq": 3, "value": 71.5653, "ts": "..."}
# {"seq": 4, "value": 2.1583,  "ts": "..."}
# {"seq": 5, "value": 87.1441, "ts": "..."}
```

In API Dash: pick `StreamTicks` after **Reflect**, send the single request, and
watch the responses accumulate in the stream view until the call ends. For TLS
use `localhost:9001` -- see [tls](tls.md).
