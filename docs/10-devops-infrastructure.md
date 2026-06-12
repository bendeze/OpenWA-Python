# 10 - DevOps & Infrastructure

This document outlines the operational footprint and deployment strategy for OpenWA's Hybrid Architecture.

## 10.1 Production Deployment Architecture

Because OpenWA utilizes a split architecture (FastAPI Gateway + Node.js Worker), a production deployment consists of at least three distinct components.

```mermaid
flowchart TB
    subgraph ReverseProxy["Ingress"]
        NGINX[Nginx / Traefik]
    end
    
    subgraph CoreServices["Docker Compose Environment"]
        API[api-gateway<br/>(FastAPI/Uvicorn)]
        WORKER[wa-worker<br/>(Node.js/Puppeteer)]
        REDIS[(Redis Server)]
    end
    
    NGINX --> API
    API <--> REDIS
    REDIS <--> WORKER
```

### Components

1. **`api-gateway` (Python)**: The lightweight FastAPI process serving HTTP traffic. Requires minimal RAM.
2. **`wa-worker` (Node.js)**: The heavy engine. It spawns headless Chromium instances for `whatsapp-web.js`. Requires significant RAM (~300-500MB per active session).
3. **`redis`**: The central nervous system. Handles all cross-container IPC (Inter-Process Communication) via Pub/Sub.

## 10.2 Docker Compose (Standard Deployment)

The easiest way to deploy OpenWA is using Docker Compose.

*Note: A generic `docker-compose.yml` will be provided in the root directory in a future release.*

**Resource Allocation Rules:**
- **API Gateway**: 1 CPU Core, 256MB RAM is plenty.
- **WA Worker**: Multi-core CPU recommended. At least 1GB RAM minimum. Budget ~400MB RAM for every concurrent WhatsApp session you plan to connect.
- **Redis**: Minimal resources required (64MB RAM).

## 10.3 Environment Variables

### API Gateway (`api-gateway/.env`)
```env
# Database
DATABASE_URL=sqlite:///./openwa.db
# Alternatively for Postgres:
# DATABASE_URL=postgresql://user:password@localhost:5432/openwa

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
MASTER_API_KEY=your_super_secret_master_key
```

### WA Worker (`wa-worker/.env`)
```env
# Redis (Must point to the exact same Redis instance as the gateway!)
REDIS_URL=redis://localhost:6379/0

# Webhooks (Optional delivery configurations)
WEBHOOK_TIMEOUT=5000
```

## 10.4 CI/CD Pipeline

We enforce CI/CD checks via GitHub Actions. Every pull request must pass the comprehensive test suites before being merged:

1. **Linting**: Python `black` and `isort`, Node `prettier`.
2. **Testing**: `pytest` and `jest`.
3. **Build**: Docker image generation and layer caching tests.
