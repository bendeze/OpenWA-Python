import json
import traceback
import urllib.parse

import models
import schemas
from database import get_db
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from redis_client import redis_client, rpc_call
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/sessions/{session_id}/messages", tags=["Message"])


@router.get("")
async def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    logs = (
        db.query(models.MessageLog)
        .filter(models.MessageLog.session_id == str(session_id))
        .order_by(models.MessageLog.timestamp.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": log.msg_id,
            "session_id": log.session_id,
            "from_me": log.from_me,
            "from_str": log.from_str,
            "to_str": log.to_str,
            "body": log.body,
            "type": log.type,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


@router.post("/send-text")
async def send_message(
    session_id: int,
    payload: schemas.MessageCreate,
    api_key: str = Depends(verify_api_key),
):

    try:
        result = await rpc_call(
            "SEND_TEXT",
            {"session_id": str(session_id), "to": payload.chatId, "text": payload.text},
            timeout=60.0,
        )
        return result
    except TimeoutError:

        return JSONResponse(
            status_code=400,
            content={
                "message": "Request timed out while waiting for WhatsApp to send the message."
            },
        )
    except Exception as e:

        traceback.print_exc()

        return JSONResponse(
            status_code=400, content={"message": str(e), "type": str(type(e))}
        )


async def _send_media(session_id: int, payload: schemas.MessageMedia, action: str):

    url = payload.url
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        data = {"session_id": str(session_id), "to": payload.chatId, "url": url}
        if payload.caption:
            data["caption"] = payload.caption
        if payload.filename:
            data["filename"] = payload.filename

        result = await rpc_call(action, data, timeout=60.0)
        return result
    except TimeoutError:

        return JSONResponse(
            status_code=400,
            content={
                "message": "Request timed out while waiting for WhatsApp to send the message."
            },
        )
    except Exception as e:

        traceback.print_exc()

        return JSONResponse(
            status_code=400, content={"message": str(e), "type": str(type(e))}
        )


@router.post("/send-image")
async def send_image(
    session_id: int,
    payload: schemas.MessageMedia,
    api_key: str = Depends(verify_api_key),
):
    return await _send_media(session_id, payload, "SEND_IMAGE")


@router.post("/send-video")
async def send_video(
    session_id: int,
    payload: schemas.MessageMedia,
    api_key: str = Depends(verify_api_key),
):
    return await _send_media(session_id, payload, "SEND_VIDEO")


@router.post("/send-audio")
async def send_audio(
    session_id: int,
    payload: schemas.MessageMedia,
    api_key: str = Depends(verify_api_key),
):
    return await _send_media(session_id, payload, "SEND_AUDIO")


@router.post("/send-document")
async def send_document(
    session_id: int,
    payload: schemas.MessageMedia,
    api_key: str = Depends(verify_api_key),
):
    return await _send_media(session_id, payload, "SEND_DOCUMENT")
