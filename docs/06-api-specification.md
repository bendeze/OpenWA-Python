# 06 - API Specification

Because OpenWA utilizes **FastAPI** as the primary gateway, the API specification is dynamically generated and strictly typed out of the box using **OpenAPI (Swagger)**.

## 6.1 Interactive Documentation

You do not need to read a static Markdown file to understand the API. Once you boot the API Gateway, you can access the interactive Swagger UI directly:

1. Boot the gateway: `cd api-gateway && uvicorn main:app --port 2785`
2. Open your browser: [http://localhost:2785/docs](http://localhost:2785/docs)
3. Alternate Redoc view: [http://localhost:2785/redoc](http://localhost:2785/redoc)

From the Swagger UI, you can inject your `X-API-Key` at the top right, and then trigger test requests directly against your local backend.

## 6.2 Core Endpoints Overview

The API is grouped logically around RESTful resources.

### Sessions `/api/sessions`
- `GET /api/sessions`: List all active and disconnected sessions.
- `POST /api/sessions`: Create a new session in the database.
- `POST /api/sessions/{session_id}/start`: Publish a command to Node.js to spin up the WhatsApp engine.
- `GET /api/sessions/{session_id}/qr`: Fetch the QR code required to link the device.

### Messages `/api/sessions/{session_id}/messages`
- `GET`: Fetch recent message logs from the database.
- `POST /send-text`: Dispatch a text message to a specific JID (`1234567890@c.us`).
- `POST /send-image`: Dispatch media payloads.

### Authentication `/api/auth`
- Manage API Keys to restrict who can talk to the Gateway.

## 6.3 Pydantic Schemas

Under the hood, all inbound data structures are mapped via Pydantic (`api-gateway/schemas.py`). 

Example inbound payload for creating a session:
```python
from pydantic import BaseModel

class SessionCreate(BaseModel):
    name: str
```
If a user attempts to `POST /api/sessions` with `{"name": 123}`, FastAPI will automatically reject it with a typed `422 Unprocessable Entity` validation error before the controller ever fires.
