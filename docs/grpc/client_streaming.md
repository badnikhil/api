---
protocol: grpc
title: gRPC Client Streaming
desc: A stream of requests, one response. SumNumbers consumes the numbers you stream and returns their sum, count and average.
path: grpc/client_streaming
---

In a **client-streaming** call the client sends a **stream** of request messages
and the server returns a **single** response once the client has finished
sending. It is the inverse of [server streaming](server_streaming.md).

`apidash.test.TestService` exposes one client-streaming method:

- `SumNumbers` -- consumes a stream of `NumberRequest{value}` messages and, once
  you half-close, returns one `SumResponse` with the `sum`, `count` and
  `average` of everything you sent.

## What it tests

That API Dash can open a request stream, send several messages, then
**half-close** (signal "done sending") and receive the single aggregated
response.

## Method

```
apidash.test.TestService/SumNumbers    # stream of NumberRequest{value} -> SumResponse{sum, count, average}
```

## Expected behavior

| Request (stream) | Response |
| ----------- | ----------- |
| `{"value":1.5}`, `{"value":2.5}`, `{"value":4.0}`, `{"value":12.0}` | `{"sum": 20.0, "count": 4, "average": 5.0}` after you finish sending |
| (no messages, immediate half-close) | `{"sum": 0, "count": 0, "average": 0}` |

The single response is only sent **after** the client closes its side of the
stream.

## Test it in API Dash

1. **Reflect** against `localhost:9000` and pick
   `apidash.test.TestService/SumNumbers`.
2. Add several messages to the request stream -- e.g. `{"value": 1.5}`,
   `{"value": 2.5}`, `{"value": 4.0}`, `{"value": 12.0}`.
3. **Finish / close** the request stream (half-close).
   - **Expected:** a single response `{"sum": 20, "count": 4, "average": 5}`.

## Sample Usage

### grpcurl

grpcurl reads a stream of request messages from stdin -- separate JSON objects
are sent as separate messages, and EOF (Ctrl-D) half-closes the stream:

```
grpcurl -plaintext -d @ localhost:9000 apidash.test.TestService/SumNumbers <<'EOF'
{"value": 1.5}
{"value": 2.5}
{"value": 4.0}
{"value": 12.0}
EOF
# {
#   "sum": 20,
#   "count": 4,
#   "average": 5
# }
```

The `-d @` tells grpcurl to read the message stream from stdin. In API Dash: add
several messages to the request stream, then finish/close the stream to get the
single response. For TLS use `localhost:9001` -- see [tls](tls.md).
