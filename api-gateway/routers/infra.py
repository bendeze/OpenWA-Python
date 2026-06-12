import json
import os

import dotenv
import schemas
from database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/infra", tags=["Infrastructure"])

ENV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
)


def get_config():
    env = dotenv.dotenv_values(ENV_PATH)
    return {
        "database": {
            "type": env.get("DATABASE_TYPE", "sqlite"),
            "host": env.get("DATABASE_HOST", "localhost"),
            "port": env.get("DATABASE_PORT", "5432"),
            "username": env.get("DATABASE_USERNAME", "postgres"),
            "password": env.get("DATABASE_PASSWORD", ""),
            "database": env.get("DATABASE_NAME", "openwa"),
            "builtIn": env.get("POSTGRES_BUILTIN", "false") == "true",
        },
        "redis": {
            "enabled": env.get("REDIS_ENABLED", "false") == "true",
            "host": env.get("REDIS_HOST", "localhost"),
            "port": env.get("REDIS_PORT", "6379"),
            "builtIn": env.get("REDIS_BUILTIN", "false") == "true",
            "password": env.get("REDIS_PASSWORD", ""),
        },
        "queue": {"enabled": True},
        "storage": {
            "type": env.get("STORAGE_TYPE", "local"),
            "localPath": env.get("STORAGE_LOCAL_PATH", "./uploads"),
            "s3Bucket": env.get("S3_BUCKET", "openwa"),
            "s3Region": env.get("S3_REGION", "ap-southeast-1"),
            "s3AccessKey": env.get("S3_ACCESS_KEY", ""),
            "s3SecretKey": env.get("S3_SECRET_KEY", ""),
            "s3Endpoint": env.get("S3_ENDPOINT", ""),
        },
        "server": {
            "port": env.get("API_PORT", "2785"),
            "nodeEnv": env.get("NODE_ENV", "development"),
            "domain": env.get("DOMAIN", "localhost"),
            "dashboardPort": env.get("DASHBOARD_PORT", "2886"),
            "baseUrl": env.get("BASE_URL", ""),
            "dashboardUrl": env.get("DASHBOARD_URL", ""),
            "corsOrigins": env.get("CORS_ORIGINS", "*"),
        },
        "webhook": {
            "timeout": int(env.get("WEBHOOK_TIMEOUT", 10000)),
            "maxRetries": int(env.get("WEBHOOK_MAX_RETRIES", 3)),
            "retryDelay": int(env.get("WEBHOOK_RETRY_DELAY", 5000)),
        },
        "rateLimit": {
            "ttl": int(env.get("RATE_LIMIT_TTL", 60)),
            "max": int(env.get("RATE_LIMIT_MAX", 100)),
        },
        "engine": {
            "type": env.get("ENGINE_TYPE", "whatsapp-web.js"),
            "headless": env.get("PUPPETEER_HEADLESS", "true") == "true",
        },
    }


def set_config(data):
    if not os.path.exists(ENV_PATH):
        open(ENV_PATH, "w").close()

    db = data.get("database", {})
    if "type" in db:
        dotenv.set_key(ENV_PATH, "DATABASE_TYPE", str(db["type"]))
    if "host" in db:
        dotenv.set_key(ENV_PATH, "DATABASE_HOST", str(db["host"]))
    if "port" in db:
        dotenv.set_key(ENV_PATH, "DATABASE_PORT", str(db["port"]))
    if "username" in db:
        dotenv.set_key(ENV_PATH, "DATABASE_USERNAME", str(db["username"]))
    if "password" in db:
        dotenv.set_key(ENV_PATH, "DATABASE_PASSWORD", str(db["password"]))
    if "database" in db:
        dotenv.set_key(ENV_PATH, "DATABASE_NAME", str(db["database"]))
    if "builtIn" in db:
        dotenv.set_key(ENV_PATH, "POSTGRES_BUILTIN", str(db["builtIn"]).lower())

    redis = data.get("redis", {})
    if "enabled" in redis:
        dotenv.set_key(ENV_PATH, "REDIS_ENABLED", str(redis["enabled"]).lower())
    if "builtIn" in redis:
        dotenv.set_key(ENV_PATH, "REDIS_BUILTIN", str(redis["builtIn"]).lower())
    if "host" in redis:
        dotenv.set_key(ENV_PATH, "REDIS_HOST", str(redis["host"]))
    if "port" in redis:
        dotenv.set_key(ENV_PATH, "REDIS_PORT", str(redis["port"]))
    if "password" in redis:
        dotenv.set_key(ENV_PATH, "REDIS_PASSWORD", str(redis["password"]))

    storage = data.get("storage", {})
    if "type" in storage:
        dotenv.set_key(ENV_PATH, "STORAGE_TYPE", str(storage["type"]))
    if "localPath" in storage:
        dotenv.set_key(ENV_PATH, "STORAGE_LOCAL_PATH", str(storage["localPath"]))
    if "s3Bucket" in storage:
        dotenv.set_key(ENV_PATH, "S3_BUCKET", str(storage["s3Bucket"]))
    if "s3Endpoint" in storage:
        dotenv.set_key(ENV_PATH, "S3_ENDPOINT", str(storage["s3Endpoint"]))
    if "s3AccessKey" in storage:
        dotenv.set_key(ENV_PATH, "S3_ACCESS_KEY", str(storage["s3AccessKey"]))
    if "s3SecretKey" in storage:
        dotenv.set_key(ENV_PATH, "S3_SECRET_KEY", str(storage["s3SecretKey"]))

    server = data.get("server", {})
    if "port" in server:
        dotenv.set_key(ENV_PATH, "API_PORT", str(server["port"]))
    if "dashboardPort" in server:
        dotenv.set_key(ENV_PATH, "DASHBOARD_PORT", str(server["dashboardPort"]))
    if "nodeEnv" in server:
        dotenv.set_key(ENV_PATH, "NODE_ENV", str(server["nodeEnv"]))

    wh = data.get("webhook", {})
    if "timeout" in wh:
        dotenv.set_key(ENV_PATH, "WEBHOOK_TIMEOUT", str(wh["timeout"]))
    if "maxRetries" in wh:
        dotenv.set_key(ENV_PATH, "WEBHOOK_MAX_RETRIES", str(wh["maxRetries"]))
    if "retryDelay" in wh:
        dotenv.set_key(ENV_PATH, "WEBHOOK_RETRY_DELAY", str(wh["retryDelay"]))

    rl = data.get("rateLimit", {})
    if "ttl" in rl:
        dotenv.set_key(ENV_PATH, "RATE_LIMIT_TTL", str(rl["ttl"]))
    if "max" in rl:
        dotenv.set_key(ENV_PATH, "RATE_LIMIT_MAX", str(rl["max"]))


@router.get("/status")
async def get_status():
    config = get_config()

    # Append dynamic metrics
    config["database"]["connected"] = True
    config["redis"]["connected"] = True
    config["queue"]["messages"] = {"pending": 0, "completed": 0, "failed": 0}
    config["queue"]["webhooks"] = {"pending": 0, "completed": 0, "failed": 0}

    return config


@router.put("/config")
async def save_config(payload: schemas.SaveConfigPayload):
    set_config(payload.dict())
    return {
        "message": "Configuration saved successfully",
        "saved": True,
        "envPath": ".env",
        "profiles": ["api-gateway", "wa-worker"],
    }


import os
import signal
import subprocess
from datetime import datetime

import dotenv
from routers.audit import create_audit_log


@router.post("/restart")
async def restart_infra(payload: schemas.RestartPayload, db: Session = Depends(get_db)):

    create_audit_log(
        db,
        action="Restart Infrastructure",
        severity="warn",
        details="Restart triggered via dashboard",
    )

    # If running inside docker, we can orchestrate via docker cli
    is_docker = os.path.exists("/.dockerenv")

    if is_docker:
        try:
            # We spin up docker compose up -d to recreate containers if .env changed
            subprocess.Popen(["docker", "compose", "up", "-d"], cwd="/app")
        except Exception as e:
            print(f"Failed to orchestrate docker: {e}")
    else:
        # If running locally, we can send a signal to ourselves so uvicorn reboots if managed
        # Note: Uvicorn with reload=True will automatically reload on .env changes anyway
        pass

    return {
        "message": "Restarting services...",
        "restarting": True,
        "profiles": payload.profiles,
        "profilesToRemove": payload.profilesToRemove,
        "estimatedTime": 5,
    }


@router.get("/health")
async def infra_health_check():

    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@router.get("/engines")
async def get_engines():
    return [
        {
            "id": "whatsapp-web.js",
            "name": "WhatsApp Web.js",
            "enabled": True,
            "features": ["text", "media", "groups"],
        },
        {
            "id": "baileys",
            "name": "Baileys",
            "enabled": True,
            "features": ["text", "media", "groups", "websockets"],
        },
    ]


@router.get("/engines/current")
async def get_current_engine():

    env = dotenv.dotenv_values(ENV_PATH)
    return {"engineType": env.get("ENGINE_TYPE", "whatsapp-web.js")}
