---
protocol: grpc
title: gRPC Metadata & Auth
desc: EchoMetadata reflects the request metadata (gRPC headers) back to you, so you can verify custom headers and auth-via-metadata (e.g. an authorization token) are sent.
path: grpc/metadata
---

gRPC carries key/value **metadata** (the gRPC equivalent of HTTP headers)
alongside every call. It's how clients send things like an `authorization`
token, a request id, or an API key -- gRPC has no separate "auth" mechanism, so
**auth is done via metadata**.

`apidash.test.TestService/EchoMetadata` is built for testing this: it **returns
the request metadata back to you** in the response, so you can confirm exactly
which headers API Dash put on the wire.

## What it tests

That API Dash attaches custom metadata to a gRPC call (including an
`authorization` header for auth-via-metadata) and that the values arrive at the
server intact.

## Method

```
apidash.test.TestService/EchoMetadata    # Empty -> MetadataResponse{map<string,string> metadata}
```

The request body is empty; everything interesting travels as metadata. The
response's `metadata` map contains the key/value pairs the server received.

## Expected behavior

| You send | You get back |
| ----------- | ----------- |
| Metadata `authorization: Bearer test-token` | `metadata` includes `"authorization": "Bearer test-token"` |
| Metadata `x-request-id: abc123` | `metadata` includes `"x-request-id": "abc123"` |
| No custom metadata | Only the transport's own headers (e.g. `user-agent`) come back |

This makes it a quick way to prove an auth token or any custom header is actually
being sent -- if it comes back, the server received it. (Note gRPC lowercases
metadata keys on the wire, so `Authorization` comes back as `authorization`.)

## Test it in API Dash

1. **Reflect** against `localhost:9000` and pick
   `apidash.test.TestService/EchoMetadata`.
2. Add metadata rows to the request, e.g. `authorization` / `Bearer test-token`
   and `x-request-id` / `abc123`. Leave the request body empty.
3. **Send**.
   - **Expected:** the response `metadata` map contains
     `authorization: Bearer test-token` and `x-request-id: abc123` (plus
     transport headers like `user-agent`). This is the pattern for testing
     **auth-via-metadata** against any real gRPC service.

## Sample Usage

### grpcurl

Pass metadata with `-H "key: value"` (repeatable):

```
grpcurl -plaintext \
  -H "authorization: Bearer test-token" \
  -H "x-request-id: abc123" \
  localhost:9000 apidash.test.TestService/EchoMetadata
# {
#   "metadata": {
#     "authorization": "Bearer test-token",
#     "x-request-id": "abc123",
#     "user-agent": "grpc-...",
#     ...
#   }
# }
```

In API Dash: add metadata rows to the request, call `EchoMetadata`, and confirm
the same key/value pairs appear in the response. For TLS use `localhost:9001` --
see [tls](tls.md).
