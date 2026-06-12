import asyncio
import hashlib
import hmac
import json
import logging
import uuid

import httpx
import models
import redis.asyncio as redis
import sqlalchemy.exc
from database import SessionLocal
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

REDIS_URL = "redis://127.0.0.1:6379"
redis_client = redis.from_url(
    REDIS_URL, health_check_interval=30, socket_keepalive=True
)

pending_requests = {}


async def rpc_call(action: str, payload: dict, timeout: float = 10.0):
    """Make an RPC call to the WhatsApp worker over Redis and wait for a reply."""
    req_id = str(uuid.uuid4())
    payload["action"] = action
    payload["req_id"] = req_id

    future = asyncio.get_event_loop().create_future()
    pending_requests[req_id] = future

    await redis_client.publish("wa_commands", json.dumps(payload))

    try:
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        pending_requests.pop(req_id, None)


async def send_webhook(w_url: str, w_payload: dict, w_sig: str):
    """Helper to dispatch a webhook over HTTP."""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                w_url,
                json=w_payload,
                headers={"X-Hub-Signature-256": f"sha256={w_sig}"},
            )
        except Exception as e:
            logger.error(f"Webhook dispatch to {w_url} failed: {e}")


async def dispatch_webhooks(
    db: Session, payload: dict, event_type: str, session_id_str: str
):
    """Dispatch matching webhooks for a given event."""
    webhooks = (
        db.query(models.Webhook)
        .filter(
            models.Webhook.active == True,
            models.Webhook.session_id == session_id_str,
        )
        .all()
    )
    for webhook in webhooks:
        events = webhook.events.split(",") if webhook.events else []
        if (
            event_type in events
            or "*" in events
            or "message.any" in events
            or "message" in events
        ):
            payload_bytes = json.dumps(payload).encode("utf-8")
            signature = hmac.new(
                webhook.secret.encode("utf-8"),
                payload_bytes,
                hashlib.sha256,
            ).hexdigest()
            asyncio.create_task(send_webhook(webhook.url, payload, signature))


async def handle_qr_event(data: dict, db: Session, sio):
    """Handle incoming QR code events and update the database."""
    session_id_str = str(data.get("sessionId", ""))
    if session_id_str.isdigit():
        session_db = (
            db.query(models.Session)
            .filter(models.Session.id == int(session_id_str))
            .first()
        )
        if session_db:
            session_db.status = "qr_ready"
            db.commit()
    await sio.emit("session:qr", data, namespace="/events")


async def handle_session_status(data: dict, db: Session, event: str, sio):
    """Handle session authentication and disconnection events."""
    session_id_str = str(data.get("sessionId", ""))
    if session_id_str.isdigit():
        session_db = (
            db.query(models.Session)
            .filter(models.Session.id == int(session_id_str))
            .first()
        )
        if session_db:
            session_db.status = (
                "ready" if event in ["ready", "authenticated"] else "disconnected"
            )
            if event == "ready" and data.get("phone"):
                session_db.phone = data.get("phone")
            if event == "ready" and data.get("pushname"):
                session_db.pushname = data.get("pushname")
            db.commit()
    await sio.emit("session:status", data, namespace="/events")


async def handle_message_event(data: dict, payload: dict, db: Session, sio):
    """Handle incoming messages, save to database, and dispatch webhooks."""
    msg_id = (
        data.get("id", {}).get("id")
        if isinstance(data.get("id"), dict)
        else str(data.get("id"))
    )

    log = models.MessageLog(
        session_id=data.get("session_id"),
        msg_id=msg_id,
        from_me=data.get("fromMe", False),
        from_str=data.get("from"),
        to_str=data.get("to"),
        body=data.get("body"),
        type=data.get("type"),
        timestamp=data.get("timestamp"),
    )

    try:
        db.add(log)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        logger.info(f"Message {msg_id} already exists, skipping insert.")
    except Exception as e:
        logger.error(f"Error saving message log: {e}")
        db.rollback()

    session_id_str = str(data.get("session_id")) if data.get("session_id") else None

    # Check what type the event type was originally. If not in payload, derive it.
    event_type = payload.get("event", "message")

    await dispatch_webhooks(db, payload, event_type, session_id_str)
    await sio.emit("session:message", data, namespace="/events")


async def process_wa_event(payload: dict, sio):
    """Process an event coming from the WhatsApp worker over Redis."""
    event = payload.get("event")
    data = payload.get("data", {})

    if event != "message":
        logger.info(f"[Redis Event Received] {event}")

    from plugin_manager import plugin_manager
    await plugin_manager.dispatch(event, payload)

    if event in ["qr", "ready", "authenticated", "disconnected", "message"]:
        db = SessionLocal()
        try:
            if event == "qr":
                await handle_qr_event(data, db, sio)
            elif event in ["ready", "authenticated", "disconnected"]:
                await handle_session_status(data, db, event, sio)
            elif event == "message":
                await handle_message_event(data, payload, db, sio)
        except Exception as e:
            logger.error(f"Error handling event {event}: {e}")
        finally:
            db.close()


async def process_wa_reply(payload: dict):
    """Process an RPC reply from the WhatsApp worker."""
    req_id = payload.get("req_id")
    if req_id and req_id in pending_requests:
        future = pending_requests[req_id]
        if not future.done():
            if "error" in payload and payload["error"]:
                future.set_exception(Exception(payload["error"]))
            else:
                future.set_result(payload.get("data"))


async def start_redis_listener(sio):
    """Background task to listen to Redis channels and dispatch events."""
    while True:
        pubsub = redis_client.pubsub()
        try:
            await pubsub.subscribe("wa_events", "wa_replies")
            logger.info("Started Redis listener on wa_events and wa_replies...")

            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message is not None:
                    try:
                        if message["type"] == "message":
                            channel = (
                                message["channel"].decode("utf-8")
                                if isinstance(message["channel"], bytes)
                                else message["channel"]
                            )
                            payload_str = (
                                message["data"].decode("utf-8")
                                if isinstance(message["data"], bytes)
                                else message["data"]
                            )
                            payload = json.loads(payload_str)

                            if channel == "wa_events":
                                await process_wa_event(payload, sio)
                            elif channel == "wa_replies":
                                await process_wa_reply(payload)
                    except Exception as loop_e:
                        logger.error(f"Error processing redis message: {loop_e}")
                else:
                    await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
            break
        except Exception as e:
            err_msg = str(e)
            if "Timeout reading" in err_msg or "Timeout" in err_msg:
                # Reconnect immediately for timeouts
                pass
            else:
                logger.error(
                    f"Redis listener disconnected ({e}). Reconnecting in 3s..."
                )
                await asyncio.sleep(3)
        finally:
            try:
                await pubsub.unsubscribe("wa_events", "wa_replies")
            except Exception:
                pass
            try:
                await pubsub.close()
            except Exception:
                pass
