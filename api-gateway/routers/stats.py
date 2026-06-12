from datetime import datetime, timedelta

import models
from database import get_db
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("/overview")
async def get_overview(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    # Sessions stats
    sessions = db.query(models.Session).all()
    by_status = {}
    active = 0
    for s in sessions:
        by_status[s.status] = by_status.get(s.status, 0) + 1
        if s.status == "READY":
            active += 1

    # Messages stats
    sent = db.query(models.MessageLog).filter(models.MessageLog.from_me == True).count()
    received = (
        db.query(models.MessageLog).filter(models.MessageLog.from_me == False).count()
    )

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    today_sent = (
        db.query(models.MessageLog)
        .filter(
            models.MessageLog.from_me == True,
            models.MessageLog.created_at >= today_start,
        )
        .count()
    )

    today_received = (
        db.query(models.MessageLog)
        .filter(
            models.MessageLog.from_me == False,
            models.MessageLog.created_at >= today_start,
        )
        .count()
    )

    failed = 0  # No status column in our MessageLog yet

    return {
        "sessions": {"active": active, "total": len(sessions), "byStatus": by_status},
        "messages": {
            "sent": sent,
            "received": received,
            "failed": failed,
            "today": {"sent": today_sent, "received": today_received},
        },
    }


@router.get("/messages")
async def get_message_stats(
    period: str = Query("24h"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    now = datetime.utcnow()
    if period == "24h":
        since = now - timedelta(days=1)
        format_str = "%Y-%m-%d %H:00:00"
    elif period == "7d":
        since = now - timedelta(days=7)
        format_str = "%Y-%m-%d"
    elif period == "30d":
        since = now - timedelta(days=30)
        format_str = "%Y-%m-%d"
    else:
        since = now - timedelta(days=1)
        format_str = "%Y-%m-%d %H:00:00"

    # SQLite compatible strftime
    time_series = (
        db.query(
            func.strftime(format_str, models.MessageLog.created_at).label("timestamp"),
            func.sum(func.case((models.MessageLog.from_me == True, 1), else_=0)).label(
                "sent"
            ),
            func.sum(func.case((models.MessageLog.from_me == False, 1), else_=0)).label(
                "received"
            ),
        )
        .filter(models.MessageLog.created_at >= since)
        .group_by("timestamp")
        .order_by("timestamp")
        .all()
    )

    ts_result = []
    for row in time_series:
        ts_result.append(
            {
                "timestamp": row.timestamp,
                "sent": row.sent or 0,
                "received": row.received or 0,
            }
        )

    # By session
    session_stats = (
        db.query(
            models.MessageLog.session_id,
            func.sum(func.case((models.MessageLog.from_me == True, 1), else_=0)).label(
                "sent"
            ),
            func.sum(func.case((models.MessageLog.from_me == False, 1), else_=0)).label(
                "received"
            ),
        )
        .filter(models.MessageLog.created_at >= since)
        .group_by(models.MessageLog.session_id)
        .all()
    )

    by_session = []
    for row in session_stats:
        session = (
            db.query(models.Session).filter(models.Session.id == row.session_id).first()
        )
        by_session.append(
            {
                "sessionId": str(row.session_id),
                "name": session.name if session else "Unknown",
                "sent": row.sent or 0,
                "received": row.received or 0,
            }
        )

    return {
        "timeSeries": ts_result,
        "byType": {},  # Omitted for simplicity
        "bySession": by_session,
        "topChats": [],  # Omitted for simplicity
    }


@router.get("/sessions/{session_id}")
async def get_session_stats(
    session_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    sent = (
        db.query(models.MessageLog)
        .filter(
            models.MessageLog.session_id == session_id,
            models.MessageLog.from_me == True,
        )
        .count()
    )
    received = (
        db.query(models.MessageLog)
        .filter(
            models.MessageLog.session_id == session_id,
            models.MessageLog.from_me == False,
        )
        .count()
    )

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today = (
        db.query(models.MessageLog)
        .filter(
            models.MessageLog.session_id == session_id,
            models.MessageLog.created_at >= today_start,
        )
        .count()
    )

    return {
        "session": {
            "id": str(session.id),
            "name": session.name,
            "status": session.status,
        },
        "messages": {"sent": sent, "received": received, "today": today, "failed": 0},
        "topChats": [],
        "hourlyActivity": [],
    }
