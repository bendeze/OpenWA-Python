# 18 - SDK Design

OpenWA provides official Client SDKs to make interacting with the API Gateway frictionless. We currently support **Python** and **JavaScript/TypeScript**.

## 18.1 SDK Architecture Principles

Both SDKs are designed with the following core principles:

1. **Zero Heavy Dependencies**: SDKs should not require massive framework dependencies. The JS SDK relies entirely on the native `fetch` API. The Python SDK uses standard Python classes and optionally `httpx`.
2. **Namespace Segregation**: Endpoints are grouped logically. E.g., `client.sessions.create()`, `client.messages.sendText()`.
3. **Synchronous & Asynchronous Paradigms**: Where applicable (especially in Python), both sync and async clients are exposed natively.
4. **Strong Typing**: The JS SDK is built with TypeScript and provides full interface definitions for requests and responses.

---

## 18.2 Python SDK (`sdk/python`)

The Python SDK is located in the `sdk/python/` directory.

### Installation

1. `pip install openwa-sdk`
2. `npm install @openwa/sdk` (planned)

### Server vs Client Architecture

It is crucial to understand that the SDK acts purely as a **"Remote Control"**. 

* **The OpenWA Server (The TV)**: Must be running somewhere in the world (e.g., hosted on a DigitalOcean droplet, an AWS EC2 instance, or locally via Docker). It runs the heavy WhatsApp Chromium browser and listens for HTTP requests.
* **The SDK (The Remote Control)**: A lightweight library that you install in your own separate project (like a Django app or a data analytics script). 

You simply point the SDK to your running server's IP address or domain name:

```python
from openwa import OpenWAClient

client = OpenWAClient(
    base_url="http://your-cloud-server-ip:2785", 
    api_key="your-secret-key"
)

# Sends a request over the internet to trigger the WhatsApp engine on your server
client.messages.send_text("my-session", {"chatId": "123@c.us", "text": "Hello from the SDK!"})
```

### Initialization

The SDK provides both an `OpenWAClient` for blocking operations and an `AsyncOpenWAClient` for `asyncio` workflows.

```python
from openwa import OpenWAClient, AsyncOpenWAClient

# Synchronous
client = OpenWAClient(base_url="http://localhost:2785", api_key="your_api_key")

# Asynchronous
async_client = AsyncOpenWAClient(base_url="http://localhost:2785", api_key="your_api_key")
```

### Usage Examples

**Managing Sessions:**
```python
# Create a new session
session = client.sessions.create(name="support-bot")
session_id = session["id"]

# Start the session (prompts the worker to generate a QR code)
client.sessions.start(session_id)

# Fetch the QR code
qr_data = client.sessions.get_qr(session_id)
print(qr_data["qrCode"])
```

**Sending Messages:**
```python
# Send a text message
client.messages.send_text(
    session_id=session_id,
    data={"chatId": "1234567890@c.us", "text": "Hello from Python SDK!"}
)
```

### Error Handling
The Python SDK exposes a native `OpenWAAPIError` exception that automatically parses HTTP 4xx/5xx responses from the gateway.

```python
from openwa import OpenWAAPIError

try:
    client.sessions.start("invalid-id")
except OpenWAAPIError as e:
    print(f"Error {e.status_code}: {e.message}")
```

---

## 18.3 JavaScript / TypeScript SDK (`sdk/javascript`)

The JS SDK is located in the `sdk/javascript/` directory and utilizes the native `fetch` API, meaning it runs perfectly in Node.js, Bun, Deno, and the Browser.

### Initialization

```typescript
import { OpenWAClient } from 'openwa-client';

const client = new OpenWAClient({
  baseUrl: 'http://localhost:2785',
  apiKey: 'your_api_key'
});
```

### Usage Examples

**Managing Sessions:**
```typescript
// Create a new session
const session = await client.sessions.create({ name: 'support-bot' });
const sessionId = session.id;

// Start the session
await client.sessions.start(sessionId);

// Get the sessions list
const allSessions = await client.sessions.list();
```

**Sending Messages:**
```typescript
// Send a text message
const result = await client.messages.sendText(sessionId, {
  chatId: '1234567890@c.us',
  text: 'Hello from JS SDK!'
});

console.log(result.messageId);
```

### Extending the SDKs

If you add a new route to the FastAPI Gateway (e.g., `/api/sessions/{session_id}/labels`), you must:
1. Update the Python SDK classes in `sdk/python/openwa/__init__.py`.
2. Update the TypeScript interfaces and namespaces in `sdk/javascript/src/index.ts`.
3. Add tests to both test suites.
