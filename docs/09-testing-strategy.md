# 09 - Testing Strategy

OpenWA enforces a robust testing strategy ensuring both sides of our Hybrid Architecture (Python and TypeScript) remain stable and reliable.

## 9.1 Testing Architecture

Our test suite is organized logically within the `test/` root directory to prevent cluttering the operational codebases.

```
test/
├── unit/
│   ├── api-gateway/    # FastAPI endpoint tests
│   ├── wa-worker/      # Node.js Worker logic tests
│   ├── sdk-python/     # Python Client SDK tests
│   └── sdk-javascript/ # JS Client SDK tests
└── integration/        # End-to-end multi-component tests
```

## 9.2 Python Testing (Pytest)

We use **pytest** for testing the API Gateway, the Python SDK, and the End-to-End integration workflows.

### Running the Python Suites

```bash
# Export PYTHONPATH so the tests can import the modules natively
PYTHONPATH=$(pwd) api-gateway/venv/bin/pytest test/unit/api-gateway/ test/unit/sdk-python/ test/integration/
```

### Fixtures & Mocking
- **Database (`db_session`)**: Located in `test/conftest.py`, we inject a fully isolated in-memory SQLite database (`StaticPool`) into every test. The database is wiped clean automatically after each function execution.
- **FastAPI Client (`client`)**: We use FastAPI's `TestClient` allowing us to perform synchronous HTTP requests against the endpoints without booting a live Uvicorn server.
- **Mocker (`pytest-mock`)**: We heavily utilize the `mocker` fixture to patch external dependencies like `redis_client.publish`. Since the architecture is decoupled via Redis, we can test the API by simply asserting that the correct Redis payloads are dispatched!

*Note: Be sure to use `mocker.AsyncMock` when patching async functions!*

## 9.3 TypeScript Testing (Jest)

We use **Jest** paired with `ts-jest` for testing the JS SDK and the `wa-worker` logic.

### Running the TypeScript Suites

Because the `test/` directory lives *outside* the `wa-worker` and `sdk/javascript` package roots, Jest is configured via `roots` and `transform` mappings in `jest.config.js` to transpile the tests correctly.

```bash
# Test the Worker
cd wa-worker
npx jest

# Test the JS SDK
cd sdk/javascript
npx jest
```

### Mocking in Jest
- The JS SDK tests mock the global `fetch` API.
- The `wa-worker` tests mock the `whatsapp-web.js` event emitters and `ioredis` subscriptions.

## 9.4 Integration Tests

The `test/integration/` directory contains tests that boot the actual FastAPI application, inject an in-memory database, mock the Node.js Redis responses, and use the **Python SDK** to interact with the API Gateway.

This ensures that:
1. The API Gateway routes correctly.
2. The Database persists state.
3. The internal RPC and Pub/Sub mechanics function as expected.
4. The SDK correctly parses the responses.

All four of these layers are verified in a single `test_e2e_flow.py` execution.
