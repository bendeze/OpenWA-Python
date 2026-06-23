<div align="center">
  <img src="https://raw.githubusercontent.com/bendeze/OpenWA-Python/main/docs/logo/openwa_logo.png" alt="OpenWA Logo" width="200"/>
  <h1>OpenWA Python SDK</h1>
  <p>The official, high-performance Python client library for the <a href="https://github.com/bendeze/OpenWA-Python">OpenWA-Python</a> REST API Gateway.</p>

  <p>
    <a href="https://pypi.org/project/openwa-sdk/"><img src="https://img.shields.io/pypi/v/openwa-sdk.svg?style=flat-square" alt="PyPI version" /></a>
    <a href="https://pypi.org/project/openwa-sdk/"><img src="https://img.shields.io/pypi/pyversions/openwa-sdk.svg?style=flat-square" alt="Python Versions" /></a>
    <a href="https://github.com/bendeze/OpenWA-Python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/bendeze/openwa-python?style=flat-square" alt="License" /></a>
  </p>
</div>

---

## Overview

The **OpenWA Python SDK** provides a seamless, developer-friendly interface to manage WhatsApp sessions, send text/media messages, register webhooks, and interact with WhatsApp groups natively in Python.

Built entirely around the [OpenWA OpenAPI specification](https://github.com/bonheurNE07/OpenWA-Python), this SDK abstracts away HTTP requests and JSON parsing, delivering a fully-typed and intuitive developer experience.

## Key Features

- **🚀 Synchronous & Asynchronous**: Ships with both blocking (`OpenWAClient`) and non-blocking (`AsyncOpenWAClient`) implementations out of the box via HTTPX.
- **🛡️ Fully Typed**: Extensively utilizes Python type hints for unmatched IDE autocomplete and static type checking.
- **⚡ Zero Boilerplate**: Connect directly to your self-hosted OpenWA API gateway without worrying about underlying request headers, authentication protocols, or JSON serializers.
- **📦 Lightweight**: Minimal dependencies. Focuses exclusively on delivering data from the REST API to your application logic.

---

## Installation

Install the library directly from PyPI using `pip`:

```bash
pip install openwa-sdk
```

---

## Quick Start

Initialize the client with your self-hosted OpenWA Gateway Base URL and API Key.

### 1. Synchronous Usage

Ideal for standard scripts, background workers, or straightforward integrations.

```python
from openwa import OpenWAClient

# Initialize the client
client = OpenWAClient(
    base_url="http://localhost:2785", 
    api_key="your_secret_key"
)

# Create and start a new WhatsApp session
session = client.sessions.create("support_bot")
client.sessions.start(session["id"])

# Fetch the QR code for authentication
qr_data = client.sessions.qr(session["id"])
print(f"Scan this QR code in WhatsApp: {qr_data['qrCode']}")

# Send a text message to a user
client.messages.send_text(session["id"], {
    "chatId": "1234567890@c.us",
    "text": "Hello from the OpenWA Python SDK! 🐍"
})

# Mark a specific chat thread as unread
client.sessions.mark_chat_unread(session["id"], "1234567890@c.us")
```

### 2. Asynchronous Usage (Recommended for High-Concurrency)

Ideal for integration with `FastAPI`, `aiohttp`, or high-throughput bots.

```python
import asyncio
from openwa import OpenWAClient

async def main():
    # Obtain the async variant of the client
    client = OpenWAClient(
        base_url="http://localhost:2785", 
        api_key="your_secret_key"
    ).get_async_client()
    
    # Send a message asynchronously
    response = await client.messages.send_text("support_bot", {
        "chatId": "1234567890@c.us",
        "text": "Hello async world! ⚡"
    })
    
    print(f"Message sent! ID: {response['messageId']}")

asyncio.run(main())
```

---

## API Resources Reference

The `OpenWAClient` grants access to all Gateway API namespaces via grouped resources:

| Resource | Namespace | Description |
|---|---|---|
| `client.sessions` | `/api/sessions` | Create, list, start, stop, delete, and authenticate sessions. Also manage session statuses, QR codes, and chat states (`mark_chat_unread`). |
| `client.messages` | `/api/sessions/{id}/messages` | Dispatch text, media, documents, and contacts. Retrieve message history. |
| `client.contacts` | `/api/sessions/{id}/contacts` | Fetch and query contacts synced from the WhatsApp device. |
| `client.groups` | `/api/sessions/{id}/groups` | Create new groups, manage participants, fetch group metadata, and alter group subjects/settings. |
| `client.webhooks` | `/api/sessions/{id}/webhooks` | Register, update, and manage webhook subscriptions for real-time WhatsApp events. |
| `client.api_keys` | `/api/auth/api-keys` | Manage API tokens and authorization. |

> **Note:** Every resource method natively supports `await` when accessed via the `AsyncOpenWAClient`.

---

## Contributing

We welcome contributions! To set up the SDK for local development:

```bash
# Clone the repository
git clone https://github.com/bonheurNE07/OpenWA-Python.git
cd OpenWA-Python

# Install the SDK in editable mode with dev dependencies
pip install -e "sdk/python[dev]"

# Run tests
pytest test/unit/sdk-python/
```

## Support

If you encounter any bugs, have feature requests, or need general assistance, please [open an issue](https://github.com/bonheurNE07/OpenWA-Python/issues) on the main GitHub repository.

---

## License

This project is licensed under the **MIT License** - see the LICENSE file for more details.
