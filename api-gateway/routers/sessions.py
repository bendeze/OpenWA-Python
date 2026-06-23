import datetime
import json
from typing import Any, Dict, List

import models
import schemas
from database import get_db
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from redis_client import redis_client, rpc_call
from routers.audit import create_audit_log
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/sessions", tags=["Session"])


@router.post("", response_model=Dict[str, Any])
async def create_session(
    session: schemas.SessionCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Create a new WhatsApp session."""
    db_session = models.Session(name=session.name, status="created")
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    create_audit_log(
        db,
        action="Create Session",
        severity="info",
        session_id=str(db_session.id),
        details=f"Created session {session.name}",
    )

    return {
        "id": str(db_session.id),
        "name": db_session.name,
        "status": db_session.status,
        "createdAt": (
            db_session.created_at.isoformat() if db_session.created_at else None
        ),
        "lastActive": None,
    }


@router.post("/{session_id}/start", response_model=Dict[str, str])
async def start_session(
    session_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Start an existing WhatsApp session."""
    db_session = (
        db.query(models.Session).filter(models.Session.id == session_id).first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.status = "connecting"
    db.commit()

    await redis_client.publish(
        "wa_commands", json.dumps({"action": "START_SESSION", "session_id": session_id})
    )

    create_audit_log(
        db,
        action="Start Session",
        severity="info",
        session_id=str(session_id),
        details=f"Starting session {session_id}",
    )

    return {"status": "Starting session..."}


@router.post("/{session_id}/stop", response_model=Dict[str, str])
async def stop_session(
    session_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Stop an active WhatsApp session."""
    db_session = (
        db.query(models.Session).filter(models.Session.id == session_id).first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.status = "disconnected"
    db.commit()

    await redis_client.publish(
        "wa_commands", json.dumps({"action": "LOGOUT", "session_id": session_id})
    )

    create_audit_log(
        db,
        action="Stop Session",
        severity="warn",
        session_id=str(session_id),
        details=f"Stopping session {session_id}",
    )

    return {"status": "Session stopped"}


@router.get("", response_model=List[Dict[str, Any]])
async def get_sessions(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    """Retrieve all WhatsApp sessions."""
    sessions = db.query(models.Session).all()
    result = []

    for s in sessions:
        last_msg = (
            db.query(func.max(models.MessageLog.timestamp))
            .filter(models.MessageLog.session_id == str(s.id))
            .scalar()
        )
        last_active = None
        if last_msg:
            last_active = datetime.datetime.fromtimestamp(last_msg).isoformat()

        result.append(
            {
                "id": str(s.id),
                "name": s.name,
                "status": s.status,
                "phone": s.phone,
                "pushName": s.pushname,
                "createdAt": s.created_at.isoformat() if s.created_at else None,
                "lastActive": last_active,
            }
        )
    return result


@router.get("/{session_id}", response_model=Dict[str, Any])
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Retrieve a single WhatsApp session by ID."""
    s = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    last_msg = (
        db.query(func.max(models.MessageLog.timestamp))
        .filter(models.MessageLog.session_id == str(s.id))
        .scalar()
    )
    last_active = None
    if last_msg:
        last_active = datetime.datetime.fromtimestamp(last_msg).isoformat()

    return {
        "id": str(s.id),
        "name": s.name,
        "status": s.status,
        "phone": s.phone,
        "pushName": s.pushname,
        "createdAt": s.created_at.isoformat() if s.created_at else None,
        "lastActive": last_active,
    }


@router.get("/stats/overview", response_model=Dict[str, int])
async def get_session_stats(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    """Get high-level statistics for sessions."""
    total = db.query(models.Session).count()
    ready = db.query(models.Session).filter(models.Session.status == "ready").count()
    active = (
        db.query(models.Session)
        .filter(models.Session.status.in_(["ready", "authenticated"]))
        .count()
    )
    return {"total": total, "ready": ready, "active": active}


@router.delete("/{session_id}", response_model=Dict[str, str])
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Delete a WhatsApp session completely."""
    db_session = (
        db.query(models.Session).filter(models.Session.id == session_id).first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_name = db_session.name
    db.delete(db_session)
    db.commit()

    create_audit_log(
        db,
        action="Delete Session",
        severity="error",
        session_id=str(session_id),
        details=f"Deleted session {session_name}",
    )

    return {"status": "deleted"}


@router.get("/{session_id}/qr", response_model=Dict[str, Any])
async def get_session_qr(
    session_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Retrieve the QR code for a session that is connecting."""
    db_session = (
        db.query(models.Session).filter(models.Session.id == session_id).first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        qr_code = await rpc_call(
            "GET_QR_CODE", {"session_id": session_id}, timeout=15.0
        )
        return {"qrCode": qr_code, "status": db_session.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/chats/unread", response_model=Dict[str, Any])
async def mark_chat_unread(
    session_id: int,
    request: schemas.ChatUnreadRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Mark a specific chat as unread."""
    db_session = (
        db.query(models.Session).filter(models.Session.id == session_id).first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        result = await rpc_call(
            "MARK_CHAT_UNREAD",
            {"session_id": session_id, "chatId": request.chatId},
            timeout=15.0,
        )
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
