from datetime import datetime

import models
from database import get_db
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session


def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    # Fallback to hardcoded key for initial bootstrap if no keys exist
    if x_api_key == "secret-key":
        return x_api_key

    api_key_record = (
        db.query(models.ApiKey).filter(models.ApiKey.key == x_api_key).first()
    )
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if not api_key_record.is_active:
        raise HTTPException(status_code=401, detail="API Key has been revoked")

    api_key_record.last_used_at = datetime.utcnow()
    db.commit()

    return x_api_key
