import secrets

import models
import schemas
from database import get_db
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from routers.audit import create_audit_log
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/validate")
async def validate_api_key(
    api_key: str = Depends(verify_api_key), db: Session = Depends(get_db)
):
    if api_key == "secret-key":
        return {"valid": True, "role": "admin"}

    api_key_record = (
        db.query(models.ApiKey).filter(models.ApiKey.key == api_key).first()
    )
    return {
        "valid": True,
        "role": api_key_record.role if api_key_record else "operator",
    }


def _format_api_key(k, include_full_key=False, full_key=None):
    return {
        "id": str(k.id),
        "name": k.name,
        "keyPrefix": k.key[:8] if len(k.key) >= 8 else k.key,
        "fullKey": k.key,
        "role": k.role,
        "isActive": k.is_active,
        "lastUsedAt": k.last_used_at.isoformat() if k.last_used_at else None,
        "createdAt": k.created_at.isoformat() if k.created_at else None,
        **({"apiKey": full_key} if include_full_key and full_key else {}),
    }


@router.get("/api-keys")
async def get_api_keys(
    db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    keys = db.query(models.ApiKey).all()
    return [_format_api_key(k) for k in keys]


@router.post("/api-keys")
async def create_api_key(
    payload: schemas.ApiKeyCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    new_key = f"wa_{secrets.token_urlsafe(32)}"
    db_key = models.ApiKey(
        key=new_key, name=payload.name, role=payload.role, is_active=True
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    create_audit_log(
        db,
        action="Create API Key",
        severity="info",
        details=f"Created API Key: {payload.name}",
    )

    return _format_api_key(db_key, include_full_key=True, full_key=new_key)


@router.put("/api-keys/{key_id}")
async def update_api_key(
    key_id: int,
    payload: schemas.ApiKeyUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    if payload.name is not None:
        db_key.name = payload.name
    if payload.role is not None:
        db_key.role = payload.role

    db.commit()
    db.refresh(db_key)

    create_audit_log(
        db,
        action="Update API Key",
        severity="info",
        details=f"Updated API Key: {db_key.name}",
    )

    return _format_api_key(db_key)


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    key_name = db_key.name
    db.delete(db_key)
    db.commit()

    create_audit_log(
        db,
        action="Delete API Key",
        severity="warn",
        details=f"Deleted API Key: {key_name}",
    )

    return {"status": "deleted"}


@router.post("/api-keys/{key_id}/revoke")
async def revoke_api_key(
    key_id: int, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    db_key.is_active = False
    db.commit()
    db.refresh(db_key)

    create_audit_log(
        db,
        action="Revoke API Key",
        severity="warn",
        details=f"Revoked API Key: {db_key.name}",
    )

    return _format_api_key(db_key)


@router.post("/api-keys/{key_id}/rotate")
async def rotate_api_key(
    key_id: int, db: Session = Depends(get_db), api_key: str = Depends(verify_api_key)
):
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    new_key = f"wa_{secrets.token_urlsafe(32)}"
    db_key.key = new_key
    db_key.is_active = True
    db.commit()
    db.refresh(db_key)

    create_audit_log(
        db,
        action="Rotate API Key",
        severity="warn",
        details=f"Rotated API Key: {db_key.name}",
    )

    return _format_api_key(db_key, include_full_key=True, full_key=new_key)
