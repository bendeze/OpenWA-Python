# 02 - Architecture

## System Overview

OpenWA-Python follows a clean separation of concerns between the underlying WhatsApp browser/socket automation engine and the Python client layer.

```text
┌────────────────────────────────────────────────────────┐
│             UPSTREAM OPENWA ENGINE (Docker)            │
│  - Container: ghcr.io/rmyndharis/openwa                │
│  - Manages WhatsApp Web protocols & Chromium instances │
│  - Exposes REST API & Webhooks on port 3000            │
└───────────────────────────▲────────────────────────────┘
                            │
                     HTTP REST API
                            │
┌───────────────────────────▼────────────────────────────┐
│                OPENWA-PYTHON (This SDK)                │
│                                                        │
│   OpenWAClient (Sync)     AsyncOpenWAClient (Async)    │
│            │                          │                │
│            └──────────────┬───────────┘                │
│                           ▼                            │
│   ┌───────────────┬───────────────┬────────────────┐   │
│   │ sessions      │ messages      │ webhooks       │   │
│   ├───────────────┼───────────────┼────────────────┤   │
│   │ contacts      │ groups        │ api_keys       │   │
│   └───────────────┴───────────────┴────────────────┘   │
└────────────────────────────────────────────────────────┘
```

## Transport & Error Handling

- **Transport**: Built on `httpx`, providing fast connection pooling, timeouts, and native async/await support.
- **Authentication**: Uses `X-API-Key` headers passed on every request.
- **Error Mapping**: Non-2xx HTTP responses from the OpenWA engine raise an `OpenWAAPIError` containing the HTTP status code and response detail message.
