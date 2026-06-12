# 11 - Operational Runbooks

These runbooks contain standard operating procedures and CLI commands for running OpenWA in a production or development environment.

## 11.1 Starting the Stack Manually

To boot OpenWA locally for development, you must run Redis, the Worker, and the API Gateway.

### 1. Redis
```bash
# Using docker
docker run -d -p 6379:6379 redis:alpine
```

### 2. Node.js Worker
```bash
cd wa-worker
npm install
npm run start
```
*Note: You must restart the worker if you make changes to `index.ts`.*

### 3. FastAPI Gateway
```bash
cd api-gateway
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Run with auto-reload for development
uvicorn main:app --port 2785 --reload
```

## 11.2 Database Migrations (Alembic)

When you modify the SQLAlchemy models in `api-gateway/models.py`, you must generate and apply migrations.

```bash
cd api-gateway
source venv/bin/activate

# Generate a new migration script
alembic revision --autogenerate -m "added new column"

# Apply the migration to SQLite/Postgres
alembic upgrade head
```

## 11.3 Running the Test Suites

OpenWA is strictly tested using Pytest and Jest.

```bash
# Run Python Unit and Integration tests
PYTHONPATH=$(pwd) api-gateway/venv/bin/pytest test/unit/api-gateway/ test/unit/sdk-python/ test/integration/

# Run Worker tests
cd wa-worker && npx jest

# Run JS SDK tests
cd sdk/javascript && npx jest
```

## 11.4 Emergency Stop

If Puppeteer gets stuck or memory leaks occur on the worker machine:

1. Send `SIGTERM` to the Node process: `pkill -f node`
2. If Zombie Chromium processes remain, force kill them: `pkill -f chromium`
3. Restart the `wa-worker` service. The API Gateway will automatically regain connectivity to the worker via Redis.
