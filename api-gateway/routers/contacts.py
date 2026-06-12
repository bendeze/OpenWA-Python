from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from redis_client import rpc_call

router = APIRouter(prefix="/api/sessions/{session_id}/contacts", tags=["Contact"])


@router.get("")
async def get_contacts(session_id: int, api_key: str = Depends(verify_api_key)):
    try:
        contacts = await rpc_call("GET_CONTACTS", {"session_id": session_id})
        return contacts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{number}")
async def check_number(
    session_id: int, number: str, api_key: str = Depends(verify_api_key)
):
    try:
        is_registered = await rpc_call(
            "CHECK_NUMBER_STATUS", {"session_id": session_id, "number": number}
        )
        return {
            "number": number,
            "exists": is_registered,
            "whatsappId": f"{number}@c.us" if is_registered else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}")
async def get_contact(
    session_id: int, contact_id: str, api_key: str = Depends(verify_api_key)
):
    try:
        contact = await rpc_call(
            "GET_CONTACT_BY_ID", {"session_id": session_id, "contact_id": contact_id}
        )
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{contact_id}/block")
async def block_contact(
    session_id: int, contact_id: str, api_key: str = Depends(verify_api_key)
):
    try:
        await rpc_call(
            "BLOCK_CONTACT", {"session_id": session_id, "contact_id": contact_id}
        )
        return {"success": True, "message": "Contact blocked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
