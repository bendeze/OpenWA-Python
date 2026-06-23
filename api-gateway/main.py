"""
OpenWA API Gateway Entrypoint.

This module initializes the FastAPI application, mounts the Socket.IO server,
and includes all router endpoints for the OpenWA backend.
"""

import asyncio
from contextlib import asynccontextmanager

import models
import schemas
import socketio
import uvicorn
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, Header, HTTPException
from redis_client import redis_client, start_redis_listener
from sqlalchemy.orm import Session

# Create database tables
Base.metadata.create_all(bind=engine)

# Create a global Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.on("connect", namespace="/events")
async def on_connect(sid, environ, auth=None):
    """Handle Socket.IO client connections."""
    print(f"Socket.IO client connected to /events: {sid}")


@sio.on("disconnect", namespace="/events")
async def on_disconnect(sid):
    """Handle Socket.IO client disconnections."""
    print(f"Socket.IO client disconnected from /events: {sid}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    listener_task = asyncio.create_task(start_redis_listener(sio))
    yield
    # Shutdown
    listener_task.cancel()
    await redis_client.close()


app = FastAPI(title="OpenWA Python API Gateway", lifespan=lifespan)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

from routers import (
    api_keys,
    audit,
    auth,
    catalog,
    contacts,
    groups,
    health,
    infra,
    messages,
    plugins,
    sessions,
    stats,
    webhooks,
)

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(messages.router)
app.include_router(webhooks.router)
app.include_router(api_keys.router)
app.include_router(contacts.router)
app.include_router(groups.router)
app.include_router(catalog.router)
app.include_router(health.router)
app.include_router(audit.router)
app.include_router(stats.router)
app.include_router(infra.router)
app.include_router(plugins.router)

if __name__ == "__main__":
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
