---
protocol: grpc
title: gRPC Bidirectional Streaming
desc: Both sides stream at once. Chat echoes each message you send straight back with a server timestamp -- a full-duplex round-trip.
path: grpc/bidi
---

In a **bidirectional-streaming** call both sides stream messages at the same
time over one long-lived HTTP/2 channel: the client can keep sending while the
server keeps replying, in any interleaving, until either side closes. It is the
richest gRPC call type and the closest analogue to a WebSocket.

`apidash.test.TestService` exposes one bidi method:

- `Chat` -- **echoes** each `ChatMessage` you send straight back on the response
  stream, filling in the `ts` field with the server's timestamp so you can see
  the server touched each reply.

## What it tests

That API Dash can hold a full-duplex stream open, send and receive messages
concurrently, and shut the channel down cleanly.

## Method

```
apidash.test.TestService/Chat    # stream ChatMessage{user, text} <-> stream ChatMessage{user, text, ts}
```

## Expected behavior

| You send | You receive |
| ----------- | ----------- |
| `{"user":"nikhil","text":"hi"}` | `{"user":"nikhil","text":"hi","ts":"2026-...Z"}` -- echoed back with a server `ts` |
| `{"user":"bot","text":"testing bidi"}` | `{"user":"bot","text":"testing bidi","ts":"..."}` |

Because it is full-duplex, a reply can arrive before you have finished sending;
the response stream ends when you half-close the request stream.

## Test it in API Dash

1. **Reflect** against `localhost:9000` and pick `apidash.test.TestService/Chat`.
2. Send a message, e.g. `{"user": "nikhil", "text": "hi"}`.
   - **Expected:** the server immediately echoes back `{"user":"nikhil",
     "text":"hi","ts":"<server time>"}`.
3. Send two or three more; each is echoed back in order with its own `ts`.
4. **Close** the stream to end the call.

## Sample Usage

### grpcurl

grpcurl sends each stdin JSON object as a message and prints replies as they
arrive; EOF closes the client side:

```
grpcurl -plaintext -d @ localhost:9000 apidash.test.TestService/Chat <<'EOF'
{"user": "nikhil", "text": "hi"}
{"user": "nikhil", "text": "how are you"}
{"user": "bot", "text": "testing bidi"}
EOF
# {"user": "nikhil", "text": "hi", "ts": "2026-08-23T19:53:15.431275+00:00"}
# {"user": "nikhil", "text": "how are you", "ts": "..."}
# {"user": "bot", "text": "testing bidi", "ts": "..."}
```

In API Dash: open `Chat`, send messages one at a time and watch replies stream
back, then close the stream to end the call. For TLS use `localhost:9001` -- see
[tls](tls.md).
