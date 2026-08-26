---
protocol: grpc
title: gRPC Server Reflection
desc: The test server has reflection enabled, so API Dash's Reflect button lists apidash.test.TestService and all seven methods with no .proto file needed.
path: grpc/reflection
---

The test server has **server reflection** enabled, so a client can ask the
server which services and methods it exposes -- and their message shapes --
**without a `.proto` file**. This is what API Dash's **Reflect** button uses to
populate the method list.

Reflection is served by the `grpc.reflection.v1alpha.ServerReflection` service.
Its single method, `ServerReflectionInfo`, is itself a bidirectional stream: the
client sends queries ("list services", "give me the descriptor for this symbol")
and the server streams back Protobuf descriptors.

> **Version note:** the server registers the standard **v1alpha** reflection
> service (what the `grpc-reflection` package ships). There is a newer
> `grpc.reflection.v1.ServerReflection`; API Dash tries `v1` first and **falls
> back to `v1alpha`**, so Reflect works transparently.

## What it tests

That API Dash can discover services/methods over reflection and drive requests
from the returned descriptors alone -- no manually imported schema.

## Method

```
grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo
```

## Expected behavior

| Query | Result |
| ----------- | ----------- |
| List services | `apidash.test.TestService` (and the reflection service itself) |
| Describe `apidash.test.TestService` | Descriptors for `Echo`, `GetRandomUser`, `StreamTicks`, `SumNumbers`, `Chat`, `EchoMetadata`, `RaiseError` |
| Describe a message (e.g. `apidash.test.User`) | Its field descriptors (`id`, `name`, `email`, `age`, `country`) |

## Test it in API Dash

1. Point the request at `localhost:9000` (TLS off).
2. Hit **Reflect** -- the service/method tree populates with
   `apidash.test.TestService` and its **seven** methods.
3. Pick any method and its request message is pre-filled from the descriptor
   (e.g. `Echo` shows a `message` field).

**Expected:** exactly one application service, `apidash.test.TestService`, with
the seven methods above, plus the reflection service.

## Sample Usage

### grpcurl

List all services:

```
grpcurl -plaintext localhost:9000 list
# apidash.test.TestService
# grpc.reflection.v1alpha.ServerReflection
```

List the methods on the service:

```
grpcurl -plaintext localhost:9000 list apidash.test.TestService
# apidash.test.TestService.Chat
# apidash.test.TestService.Echo
# apidash.test.TestService.EchoMetadata
# apidash.test.TestService.GetRandomUser
# apidash.test.TestService.RaiseError
# apidash.test.TestService.StreamTicks
# apidash.test.TestService.SumNumbers
```

Describe a method or message:

```
grpcurl -plaintext localhost:9000 describe apidash.test.TestService.Echo
grpcurl -plaintext localhost:9000 describe apidash.test.User
```

All of the above use reflection (there is no `-proto`/`-import-path` flag), which
is exactly the path API Dash's **Reflect** takes. For the TLS listener, drop
`-plaintext` and add `-insecure` against `localhost:9001` -- see [tls](tls.md).
