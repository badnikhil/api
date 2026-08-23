---
protocol: grpc
title: gRPC Errors & Status Codes
desc: RaiseError fails the call with the gRPC status code you request, so you can test how API Dash surfaces non-OK statuses and their messages.
path: grpc/errors
---

gRPC calls don't fail with HTTP status codes -- they finish with a **gRPC status
code** (a number 0-16, e.g. `0 OK`, `3 INVALID_ARGUMENT`, `5 NOT_FOUND`,
`13 INTERNAL`, `16 UNAUTHENTICATED`) plus an optional message. Testing that API
Dash surfaces these correctly needs a server that can return them on demand.

`apidash.test.TestService/RaiseError` does exactly that:

- `RaiseError` -- deliberately fails the call with the status code **you choose**
  (via the request's `code` field), attaching your `message` as the status
  message. Ask for `5` and the call fails `NOT_FOUND`; ask for `13` and it fails
  `INTERNAL`, and so on.

## What it tests

That API Dash reads the trailing gRPC status code and message on a failed call
and shows them, instead of treating a non-OK status as a silent or generic
failure.

## Method

```
apidash.test.TestService/RaiseError    # ErrorRequest{code, message} -> fails with that status code
```

`code` is the numeric gRPC status code (e.g. `5` = `NOT_FOUND`, `13` =
`INTERNAL`); `message` becomes the status message. An out-of-range code (or `0`,
which is not an error) comes back as `2 UNKNOWN`.

## Expected behavior

| Request | Result |
| ----------- | ----------- |
| `{"code": 5, "message": "not here"}` | Call fails with status `5 NOT_FOUND`, message `not here` |
| `{"code": 13, "message": "boom"}` | Call fails with status `13 INTERNAL`, message `boom` |
| `{"code": 16, "message": "nope"}` | Call fails with status `16 UNAUTHENTICATED`, message `nope` |
| `{"code": 999}` | Call fails with status `2 UNKNOWN` (code out of range) |

There is no response message on failure -- only the status code and message
arrive as trailers.

## Test it in API Dash

1. **Reflect** against `localhost:9000` and pick
   `apidash.test.TestService/RaiseError`.
2. Set the request to `{"code": 5, "message": "not here"}` and **Send**.
   - **Expected:** the call fails and API Dash shows status **`5 NOT_FOUND`**
     with the message `not here` (not a generic error).
3. Try other codes -- `{"code": 13, "message": "boom"}` -> `13 INTERNAL`,
   `{"code": 16}` -> `16 UNAUTHENTICATED` -- to confirm each is surfaced.

## Sample Usage

### grpcurl

grpcurl prints the status code and message to stderr and exits non-zero on a
failed call:

```
grpcurl -plaintext -d '{"code": 5, "message": "not here"}' \
  localhost:9000 apidash.test.TestService/RaiseError
# ERROR:
#   Code: NotFound
#   Message: not here
```

```
grpcurl -plaintext -d '{"code": 13, "message": "boom"}' \
  localhost:9000 apidash.test.TestService/RaiseError
# ERROR:
#   Code: Internal
#   Message: boom
```

In API Dash: call `RaiseError` with a chosen `code`/`message` and confirm the
client shows that exact status. For TLS use `localhost:9001` -- see [tls](tls.md).
