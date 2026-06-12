import hashlib
import hmac
import json
import secrets
from typing import List

import httpx
import models
import schemas
from database import get_db
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from routers.audit import create_audit_log
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["Webhook"])


class WebhookCreate(schemas.BaseModel):
    url: str
    events: List[str]


class WebhookUpdate(schemas.BaseModel):
    url: str = None
    events: List[str] = None
    active: bool = None


def _format_webhook(w):
    return {
        "id": str(w.id),
        "sessionId": w.session_id,
        "url": w.url,
        "events": w.events.split(",") if w.events else [],
        "secret": w.secret,
        "active": w.active,
        "createdAt": w.created_at.isoformat() if w.created_at else None,
    }


@router.get("/webhooks")
async def get_webhooks(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    webhooks = db.query(models.Webhook).all()
    return [_format_webhook(w) for w in webhooks]


@router.post("/sessions/{session_id}/webhooks")
async def create_webhook(
    session_id: str,
    payload: WebhookCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    secret = secrets.token_urlsafe(24)
    db_webhook = models.Webhook(
        session_id=session_id,
        url=payload.url,
        events=",".join(payload.events),
        secret=secret,
        active=True,
    )
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)

    create_audit_log(
        db,
        action="Create Webhook",
        severity="info",
        session_id=session_id,
        details=f"Created webhook {payload.url}",
    )

    return _format_webhook(db_webhook)


@router.put("/sessions/{session_id}/webhooks/{webhook_id}")
async def update_webhook(
    session_id: str,
    webhook_id: int,
    payload: WebhookUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    db_webhook = (
        db.query(models.Webhook)
        .filter(
            models.Webhook.id == webhook_id, models.Webhook.session_id == session_id
        )
        .first()
    )
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if payload.url is not None:
        db_webhook.url = payload.url
    if payload.events is not None:
        db_webhook.events = ",".join(payload.events)
    if payload.active is not None:
        db_webhook.active = payload.active

    db.commit()
    db.refresh(db_webhook)

    create_audit_log(
        db,
        action="Update Webhook",
        severity="info",
        session_id=session_id,
        details=f"Updated webhook ID {webhook_id}",
    )

    return _format_webhook(db_webhook)


@router.delete("/sessions/{session_id}/webhooks/{webhook_id}")
async def delete_webhook(
    session_id: str,
    webhook_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    db_webhook = (
        db.query(models.Webhook)
        .filter(
            models.Webhook.id == webhook_id, models.Webhook.session_id == session_id
        )
        .first()
    )
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook_url = db_webhook.url
    db.delete(db_webhook)
    db.commit()

    create_audit_log(
        db,
        action="Delete Webhook",
        severity="warn",
        session_id=session_id,
        details=f"Deleted webhook {webhook_url}",
    )

    return {"status": "deleted"}


@router.post("/sessions/{session_id}/webhooks/{webhook_id}/test")
async def test_webhook(
    session_id: str,
    webhook_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    db_webhook = (
        db.query(models.Webhook)
        .filter(
            models.Webhook.id == webhook_id, models.Webhook.session_id == session_id
        )
        .first()
    )
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    payload = {
        "event": "test",
        "session_id": session_id,
        "data": {"message": "This is a test webhook payload."},
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    signature = hmac.new(
        db_webhook.secret.encode("utf-8"), payload_bytes, hashlib.sha256
    ).hexdigest()

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                db_webhook.url,
                json=payload,
                headers={"X-Hub-Signature-256": f"sha256={signature}"},
                timeout=5.0,
            )
            return {"success": True, "statusCode": res.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}
