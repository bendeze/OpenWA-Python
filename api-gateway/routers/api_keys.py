import secrets

import models
import schemas
from database import get_db
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from routers.audit import create_audit_log
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/api-keys", tags=["ApiKey"])


@router.post("", response_model=schemas.ApiKeyResponse)
async def create_api_key(
    payload: schemas.ApiKeyCreate,
    db: Session = Depends(get_db),
    current_key: str = Depends(verify_api_key),
):
    # Generate a secure random token
    new_key = f"wa_{secrets.token_urlsafe(32)}"
    db_key = models.ApiKey(key=new_key, name=payload.name, role=payload.role)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    create_audit_log(
        db,
        action="Create API Key",
        severity="info",
        details=f"Created API Key: {payload.name}",
    )

    return {
        "id": str(db_key.id),
        "key": db_key.key,
        "name": db_key.name,
        "role": db_key.role,
        "createdAt": db_key.created_at.isoformat() if db_key.created_at else None,
    }


@router.get("")
async def get_api_keys(
    db: Session = Depends(get_db), current_key: str = Depends(verify_api_key)
):
    keys = db.query(models.ApiKey).all()
    return [
        {
            "id": str(k.id),
            "key": "wa_..." + k.key[-4:],  # Mask key for security
            "name": k.name,
            "role": k.role,
            "createdAt": k.created_at.isoformat() if k.created_at else None,
        }
        for k in keys
    ]


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_key: str = Depends(verify_api_key),
):
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="API Key not found")

    key_name = db_key.name
    db.delete(db_key)
    db.commit()

    create_audit_log(
        db,
        action="Revoke API Key",
        severity="warn",
        details=f"Revoked API Key: {key_name}",
    )

    return {"status": "revoked"}
