# OpenWA Python SDK

The official Python client library for the [OpenWA-Python](https://github.com/bonheurNE07/OpenWA-Python) REST API Gateway. 

This SDK allows you to easily manage WhatsApp sessions, send text/media messages, and interact with WhatsApp groups natively in Python. It supports both **Synchronous** and **Asynchronous** workflows out of the box!

## Installation

```bash
pip install openwa-sdk
```

## Quick Start

```python
from openwa import OpenWAClient
import asyncio

# Initialize the client (points to your self-hosted OpenWA Gateway)
client = OpenWAClient(
    base_url="http://localhost:2785", 
    api_key="secret-key"
)

# --- Synchronous Example ---
# 1. Create a session
session = client.sessions.create("my-session")
print(f"Session Created: {session}")

# 2. Start the session (returns QR code in the terminal)
client.sessions.start("my-session")

# 3. Send a message
client.messages.send_text("my-session", {
    "chatId": "1234567890@c.us",
    "text": "Hello from Python!"
})

# --- Asynchronous Example ---
async def main():
    async_client = client.get_async_client()
    
    # Send a message asynchronously
    await async_client.messages.send_text("my-session", {
        "chatId": "1234567890@c.us",
        "text": "Hello async world!"
    })

asyncio.run(main())
```

## Features
* **Fully Typed**: Written with type hints for excellent IDE autocomplete.
* **Sync & Async**: Backed by `httpx`, giving you both blocking and non-blocking clients.
* **Zero Overhead**: Directly maps to the OpenWA OpenAPI specification.

## License
MIT License
