from typing import Optional

import models
from database import get_db
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("")
async def get_audit_logs(
    action: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    api_key_id: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    query = db.query(models.AuditLog)

    if action:
        query = query.filter(models.AuditLog.action == action)
    if severity:
        query = query.filter(models.AuditLog.severity == severity)
    if session_id:
        query = query.filter(models.AuditLog.session_id == session_id)
    if api_key_id:
        query = query.filter(models.AuditLog.api_key_id == api_key_id)

    total = query.count()
    logs = (
        query.order_by(models.AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    mapped_logs = []
    for log in logs:
        mapped_logs.append(
            {
                "id": str(log.id),
                "action": log.action,
                "severity": log.severity,
                "sessionId": log.session_id,
                "apiKeyName": log.api_key_id,  # Using ID as name since we don't fetch relation
                "ipAddress": "127.0.0.1",
                "createdAt": log.created_at.isoformat() + "Z",
            }
        )

    return {"data": mapped_logs, "total": total}


def create_audit_log(
    db: Session,
    action: str,
    severity: str = "info",
    session_id: str = None,
    api_key_id: str = None,
    details: str = None,
):
    try:
        new_log = models.AuditLog(
            action=action,
            severity=severity,
            session_id=session_id,
            api_key_id=api_key_id,
            details=details,
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to create audit log: {e}")
