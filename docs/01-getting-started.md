# 01 - Getting Started

This guide walks you through setting up the OpenWA engine and sending your first WhatsApp message using the Python SDK.

---

## 1. Prerequisites

- Python 3.9 or higher
- Docker & Docker Compose (for running the OpenWA engine locally)

---

## 2. Start the OpenWA Engine

Run the official OpenWA engine container using Docker Compose:

```bash
docker compose up -d
```

This starts the OpenWA server at `http://localhost:3000`. You can visit `http://localhost:3000` in your browser to access the session dashboard.

---

## 3. Install the Python SDK

Install the package directly or in editable mode for local development:

```bash
pip install openwa-sdk
# or locally:
pip install -e .
```

---

## 4. Basic Usage

### Synchronous Client

```python
from openwa import OpenWAClient

# 1. Initialize client
client = OpenWAClient(base_url="http://localhost:3000", api_key="your_api_key")

# 2. List active WhatsApp sessions
sessions = client.sessions.list()
print("Sessions:", sessions)

# 3. Send a text message
client.messages.send_text(
    session_id="default",
    data={
        "chatId": "1234567890@c.us",
        "text": "Hello from OpenWA Python!"
    }
)
```

### Asynchronous Client

```python
import asyncio
from openwa import AsyncOpenWAClient

async def main():
    async with AsyncOpenWAClient(base_url="http://localhost:3000", api_key="your_api_key") as client:
        # Create a new session
        session = await client.sessions.create("my_session")
        
        # Start the session (initializes WhatsApp connection)
        await client.sessions.start(session["id"])
        
        # Send a message
        await client.messages.send_text(
            session_id=session["id"],
            data={
                "chatId": "1234567890@c.us",
                "text": "Async message sent via OpenWA!"
            }
        )

asyncio.run(main())
```
