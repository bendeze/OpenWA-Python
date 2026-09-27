<div align="center">
  <img src="https://raw.githubusercontent.com/bendeze/OpenWA-Python/main/docs/logo/openwa_logo.png" alt="OpenWA Logo" width="200"/>
  <h1>OpenWA-Python</h1>
  <p>Official Python SDK for the <a href="https://github.com/rmyndharis/OpenWA">OpenWA</a> WhatsApp API Gateway.</p>

  <p>
    <a href="https://github.com/bendeze/openwa-python/stargazers"><img src="https://img.shields.io/github/stars/bendeze/openwa-python?style=flat-square" alt="Stars" /></a>
    <a href="https://github.com/bendeze/openwa-python/network/members"><img src="https://img.shields.io/github/forks/bendeze/openwa-python?style=flat-square" alt="Forks" /></a>
    <a href="https://github.com/bendeze/openwa-python/issues"><img src="https://img.shields.io/github/issues/bendeze/openwa-python?style=flat-square" alt="Issues" /></a>
    <a href="https://github.com/bendeze/openwa-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/bendeze/openwa-python?style=flat-square" alt="License" /></a>
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square" alt="Python Version" />
  </p>
</div>

---

## 📖 Overview

**OpenWA-Python** (`openwa-sdk`) is the Python client library for [OpenWA](https://github.com/rmyndharis/OpenWA) (the open-source, self-hosted WhatsApp API Gateway).

It provides both **synchronous** and **asynchronous** HTTP clients to interact with any running OpenWA instance:

- **Sessions**: Create, start, stop, restart, delete, check status, and retrieve QR codes.
- **Messages**: Send text, images, files, locations, contacts, polls, reactions, and replies.
- **Webhooks**: Register, inspect, and manage webhook endpoints.
- **Contacts**: List, fetch, block, and unblock contacts.
- **Groups**: List, fetch, create, leave groups, and manage participants.
- **API Keys**: Manage authenticated API keys.

---

## 🚀 Quickstart

### 1. Start the OpenWA Engine

Run the official OpenWA engine container for local development:

```bash
docker compose up -d
```
The OpenWA REST API and dashboard will be available at `http://localhost:3000`.

### 2. Install the Python SDK

```bash
pip install openwa-sdk
# or install from source in editable mode:
pip install -e .
```

### 3. Synchronous Client Usage

```python
from openwa import OpenWAClient

# Initialize client
client = OpenWAClient(base_url="http://localhost:3000", api_key="your_api_key")

# List sessions
sessions = client.sessions.list()
print("Active sessions:", sessions)

# Send a text message
client.messages.send_text(
    session_id="default",
    data={
        "chatId": "1234567890@c.us",
        "text": "Hello from OpenWA-Python! 🚀"
    }
)
```

### 4. Asynchronous Client Usage

```python
import asyncio
from openwa import AsyncOpenWAClient

async def main():
    async with AsyncOpenWAClient(base_url="http://localhost:3000", api_key="your_api_key") as client:
        # Create and start a session
        session = await client.sessions.create("my_session")
        await client.sessions.start(session["id"])
        
        # Send a message
        response = await client.messages.send_text(
            session_id=session["id"],
            data={"chatId": "1234567890@c.us", "text": "Async message!"}
        )
        print("Message sent:", response)

asyncio.run(main())
```

---

## 📚 SDK Reference

### Available Resources

| Resource | Method Examples |
| :--- | :--- |
| `client.sessions` | `.list()`, `.create(name)`, `.start(id)`, `.stop(id)`, `.qr(id)`, `.status(id)` |
| `client.messages` | `.send_text(id, data)`, `.send_image(id, data)`, `.send_file(id, data)`, `.reply(id, data)` |
| `client.webhooks` | `.list()`, `.create(data)`, `.delete(id)` |
| `client.contacts` | `.list(session_id)`, `.get(session_id, contact_id)`, `.block(session_id, contact_id)` |
| `client.groups` | `.list(session_id)`, `.create(session_id, data)`, `.add_participants(session_id, group_id, data)` |
| `client.api_keys` | `.list()`, `.create(data)`, `.delete(id)` |

---

## 🧪 Development & Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/

# Format code
black openwa/ tests/ examples/
isort openwa/ tests/ examples/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///home/bonheur/openwa_python/LICENSE) file for details.
