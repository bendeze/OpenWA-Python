# 08 - Development Guidelines

This document outlines the coding standards, workflow, and architecture principles for contributing to OpenWA.

Since OpenWA utilizes a **Hybrid Architecture** (Python + TypeScript), we adhere to the standard conventions of both ecosystems.

## 8.1 Python Development (API Gateway & SDK)

The API Gateway is built with **FastAPI** and the Python SDK is built standard Python HTTP libraries.

### Environment Management
Always use a Python virtual environment to isolate dependencies.

```bash
cd api-gateway
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Code Formatting
We enforce strictly formatted code to prevent bikeshedding in code reviews.

1. **Black**: The uncompromising Python code formatter.
2. **Isort**: Sorts imports alphabetically and automatically separates them into sections.

**Usage:**
```bash
black api-gateway/ sdk/python/ test/
isort api-gateway/ sdk/python/ test/
```

### Typing
All Python code must use type hints. This enables FastAPI to automatically generate OpenAPI documentation and perform Pydantic validation.

```python
# DO THIS:
def create_session(name: str) -> dict: ...

# DON'T DO THIS:
def create_session(name): ...
```

## 8.2 Node.js Development (WA Worker & JS SDK)

The WhatsApp Engine worker (`wa-worker`) and the JS SDK are written in **TypeScript**.

### Environment Management

```bash
cd wa-worker
npm install
```

### Code Formatting
We use **Prettier** for formatting all TypeScript and JavaScript code.

**Usage:**
```bash
npx prettier --write "wa-worker/src/**/*.ts"
npx prettier --write "sdk/javascript/src/**/*.ts"
```

### TypeScript Strict Mode
We enforce `strict: true` in our `tsconfig.json`. This means:
- No implicit `any`
- Strict null checks
- Strict function types

## 8.3 Git Workflow

### Branch Naming Convention
- `feature/short-description` (e.g., `feature/postgres-support`)
- `fix/short-description` (e.g., `fix/redis-timeout`)
- `docs/short-description` (e.g., `docs/update-architecture`)

### Commit Messages
We follow conventional commits:
```
feat: add multi-session support
fix: resolve database connection leak
docs: update readme with quickstart
test: add pytest for sessions router
```

## 8.4 Best Practices

1. **Keep the Gateway Dumb**: The FastAPI gateway should only validate requests, update the database, and publish to Redis. It should never perform heavy blocking CPU operations or attempt to parse WhatsApp-specific binary protocols.
2. **Fail Fast in Python**: Use Pydantic to validate all incoming data structures so that malformed requests are rejected with a `422 Unprocessable Entity` before they ever reach the Node.js worker.
3. **Graceful Shutdown**: The Node.js worker must gracefully close Puppeteer browsers when it receives a `SIGTERM` to prevent memory leaks and orphaned zombie processes.
