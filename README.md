<div align="center">
  <img src="https://github.com/bonheurNE07/OpenWA-Python/blob/main/docs%2Flogo%2Fopenwa_logo.png" alt="OpenWA Logo" width="200"/>
  <h1>OpenWA-Python</h1>
  <p>The free, open-source, production-ready WhatsApp REST API Gateway.</p>

  <p>
    <a href="https://github.com/yourusername/openwa-python/stargazers"><img src="https://img.shields.io/github/stars/bonheurNE07/openwa-python?style=flat-square" alt="Stars" /></a>
    <a href="https://github.com/yourusername/openwa-python/network/members"><img src="https://img.shields.io/github/forks/bonheurNE07/openwa-python?style=flat-square" alt="Forks" /></a>
    <a href="https://github.com/yourusername/openwa-python/issues"><img src="https://img.shields.io/github/issues/bonheurNE07/openwa-python?style=flat-square" alt="Issues" /></a>
    <a href="https://github.com/bonheurNE07/openwa-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/bonheurNE07/openwa-python?style=flat-square" alt="License" /></a>
  </p>
</div>

> **Notice**: **OpenWA-Python** is a Python/FastAPI adaptation of the incredible [OpenWA](https://github.com/rmyndharis/OpenWA) project. While the original uses a pure Node.js/NestJS monolith, this fork restructures the backend into a Hybrid Architecture (FastAPI API Gateway + Node.js Worker) for developers who want to integrate WhatsApp natively into Python ecosystems.

## What is OpenWA-Python?

**OpenWA-Python** is a powerful HTTP API gateway for WhatsApp. It allows developers to send messages, manage sessions, and receive webhooks without touching complex headless browser automation or paying expensive monthly fees to third-party services.

### The Hybrid Architecture Advantage
OpenWA combines the best of two ecosystems:
- 🐍 **FastAPI (Python)**: Provides the high-performance HTTP Gateway, Swagger documentation, and database interaction via SQLAlchemy.
- 🟢 **Node.js**: Runs the underlying `whatsapp-web.js` engine and manages headless Chromium browsers.
- 🚀 **Redis**: The two layers communicate strictly over a Redis Pub/Sub event bus, meaning the API stays lightning fast even if the browser process is bogged down!

---

## Quickstart

### Prerequisites
- Python 3.12+
- Node.js 20+
- Redis Server (Running locally or via Docker)

### 1. Start Redis
```bash
# If you have Docker:
docker run -d -p 6379:6379 redis:alpine
```

### 2. Boot the Node.js Worker
```bash
cd wa-worker
npm install
npm run start
```
*The worker will connect to Redis and await commands.*

### 3. Boot the FastAPI Gateway
In a new terminal window:
```bash
cd api-gateway
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 2785
```

### 4. Open Swagger UI
Navigate to `http://localhost:2785/docs` to see the automatically generated interactive API documentation. You can create sessions, grab the QR code, and send messages directly from the browser!

---

## Client SDKs

We provide native SDKs to make interacting with the API a breeze.

### Python
```bash
pip install -e sdk/python
```
```python
from openwa import OpenWAClient

client = OpenWAClient(base_url="http://localhost:2785", api_key="secret")
client.messages.send_text("session_1", {"chatId": "123@c.us", "text": "Hello OpenWA!"})
```

### TypeScript / JavaScript
```bash
cd sdk/javascript
npm install
npm run build
```
```typescript
import { OpenWAClient } from 'openwa-client';

const client = new OpenWAClient({ baseUrl: 'http://localhost:2785', apiKey: 'secret' });
await client.messages.sendText('session_1', { chatId: '123@c.us', text: 'Hello OpenWA!' });
```

---

## Development & Testing

We enforce strict formatting and comprehensive testing to ensure stability.

```bash
# Format Python
black api-gateway/ sdk/python/ test/
isort api-gateway/ sdk/python/ test/

# Run Python Tests (API Gateway & E2E Integration)
PYTHONPATH=$(pwd) api-gateway/venv/bin/pytest test/unit/api-gateway/ test/unit/sdk-python/ test/integration/

# Run TS Tests (Worker & JS SDK)
cd wa-worker && npx jest
cd sdk/javascript && npx jest
```

---

## Documentation

Deep dive into the architecture and design decisions in the `docs/` folder:

- [01 - Project Overview](./docs/01-project-overview.md)
- [03 - System Architecture](./docs/03-system-architecture.md)
- [08 - Development Guidelines](./docs/08-development-guidelines.md)
- [09 - Testing Strategy](./docs/09-testing-strategy.md)
- [18 - SDK Design](./docs/18-sdk-design.md)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
