# 03 - System Architecture

## 3.1 Architecture Overview

### High-Level Architecture

```mermaid
flowchart TB
    subgraph Clients["Clients"]
        C1[External Apps]
        C2[Dashboard]
        C3[Python & JS SDKs]
    end
    
    subgraph OpenWA["OpenWA Platform"]
        subgraph API["API Gateway (FastAPI / Python)"]
            REST[REST API]
            SWAGGER[Swagger UI]
            AUTH[Auth Layer]
        end
        
        subgraph Bus["Message Bus"]
            REDIS[(Redis Pub/Sub)]
        end
        
        subgraph Worker["WA Worker (Node.js / TS)"]
            WW[whatsapp-web.js]
            PP[Puppeteer]
            CH[Chrome/Chromium]
        end
        
        subgraph Storage["Storage Layer"]
            DB[(Database<br/>PostgreSQL/SQLite)]
        end
    end
    
    subgraph External["External"]
        WA[WhatsApp<br/>Servers]
        WEBHOOK[Webhook<br/>Endpoints]
    end
    
    Clients --> API
    API --> DB
    API <--> |Commands & Events| REDIS
    REDIS <--> |Commands & Events| Worker
    Worker --> WA
    Worker --> WEBHOOK
```

### Component Interaction

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Gateway
    participant DB as SQLAlchemy
    participant Redis as Redis Pub/Sub
    participant Worker as Node.js Worker
    participant WA as WhatsApp
    
    Client->>API: POST /api/sessions/start
    API->>DB: Update session status to 'connecting'
    API->>Redis: Publish {"action": "START_SESSION", "session_id": 1}
    API-->>Client: 200 OK (Status: connecting)
    
    Redis-->>Worker: Receive START_SESSION event
    Worker->>WA: Initialize Puppeteer
    WA-->>Worker: QR Code ready
    Worker->>Redis: Publish {"event": "qr", "session_id": 1, "qr": "..."}
    
    Client->>API: GET /api/sessions/1/qr
    API->>Redis: RPC Request (GET_QR)
    Redis-->>API: QR String
    API-->>Client: 200 OK (QR Code data)
```

## 3.2 The Hybrid Architecture Philosophy

OpenWA shifted from a monolithic Node.js design to a **Hybrid Architecture** that explicitly divides responsibilities based on runtime strengths:

1. **API Gateway (Python/FastAPI)**: Handles HTTP requests, authentication, database storage, and input validation. Python excels at API routing, ORM abstractions (SQLAlchemy), and has massive adoption for enterprise AI/Data workloads.
2. **Message Bus (Redis)**: Acts as the strict decoupling layer. The API Gateway never calls the browser directly.
3. **Engine Worker (Node.js)**: Runs in the background, listening to Redis. It uses `whatsapp-web.js` to control headless Chromium browsers. Node.js is uniquely positioned to handle DOM manipulations, V8 engine events, and the asynchronous event loop required by Puppeteer.

### Why Decouple?

```mermaid
flowchart TB
    subgraph Philosophy["Core Design Principles"]
        P1[Memory Isolation]
        P2[Language Optimization]
        P3[Independent Scaling]
    end

    subgraph Benefits["Benefits"]
        B1[API doesn't crash when browser crashes]
        B2[Python for logic, JS for DOM]
        B3[Scale workers based on RAM]
    end

    P1 --> B1
    P2 --> B2
    P3 --> B3
```

## 3.3 Folder Structure

The repository is structured as a monorepo containing distinct logical units:

```text
OpenWA-Python/
├── api-gateway/            # Python FastAPI backend
│   ├── main.py             # Entrypoint
│   ├── models.py           # SQLAlchemy database schemas
│   ├── schemas.py          # Pydantic validation schemas
│   ├── routers/            # API Endpoints (sessions, messages, etc)
│   └── redis_client.py     # Redis RPC and Pub/Sub wrappers
│
├── wa-worker/              # Node.js TypeScript Worker
│   ├── src/index.ts        # Redis listener and WA initialization
│   ├── src/webhook.ts      # Webhook delivery system
│   └── package.json        # Dependencies (whatsapp-web.js, ioredis)
│
├── sdk/                    # Official Client Libraries
│   ├── python/             # Python SDK client
│   └── javascript/         # JS/TS SDK client
│
└── test/                   # Comprehensive Test Suite
    ├── unit/
    │   ├── api-gateway/    # Pytest unit tests for FastAPI routers
    │   ├── wa-worker/      # Jest unit tests for the worker
    │   └── sdk-*/          # Jest/Pytest unit tests for SDKs
    └── integration/        # End-to-end Python/Redis flow tests
```

## 3.4 Data Flow Diagrams

### 3.4.1 Send Message Flow

```mermaid
flowchart LR
    subgraph Client["1. Client"]
        A[External App] -->|POST /messages| B[FastAPI Gateway]
    end
    
    subgraph API["2. Gateway"]
        B --> C[Validate API Key]
        C --> D[Pydantic Validation]
        D --> E[RPC Request over Redis]
    end
    
    subgraph Worker["3. WA Worker"]
        E --> F[Listen to Command]
        F --> G[Locate WA Client]
        G --> H[Client.sendMessage()]
    end
    
    subgraph Network["4. WhatsApp Network"]
        H --> I[Meta Servers]
        I --> J[Success ACK]
    end
    
    subgraph Callback["5. Persistence"]
        J --> K[Publish 'message_ack' to Redis]
        K --> L[FastAPI consumes and saves to DB]
    end
```

### 3.4.2 Webhook Delivery Flow

When the Node.js worker detects an incoming message from the `whatsapp-web.js` event loop:

```mermaid
flowchart TB
    A[WhatsApp Message Received] --> B[Node.js Worker Event Loop]
    B --> C[Publish 'message' to Redis Pub/Sub]
    C --> D[FastAPI Background Task / Consumer]
    D --> E[Save MessageLog to SQLite/PostgreSQL]
    E --> F[Fetch Registered Webhooks]
    F --> G[POST HTTP Payload to Webhook URL]
```

## 3.5 Security Architecture

```mermaid
flowchart TB
    subgraph External["External Request"]
        R[HTTP Request]
    end
    
    subgraph GatewayLayer["FastAPI Gateway"]
        R --> HTTPS[Reverse Proxy (Nginx/Traefik)]
        HTTPS --> AUTH[API Key Dependency (`verify_api_key`)]
        AUTH --> DB[Check Key against SQLite]
        DB --> VAL[Pydantic Type Validation]
        VAL --> APP[Router Execution]
    end
```

1. **Authentication**: Handled instantly at the gateway level using FastAPI dependency injection (`Depends(verify_api_key)`).
2. **Type Safety**: All incoming JSON payloads are structurally validated by Pydantic before business logic is executed.
3. **Internal Security**: Redis is strictly used as an internal event bus. External clients never hit Redis or the Node.js worker directly.
