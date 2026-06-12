from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from redis_client import rpc_call

router = APIRouter(prefix="/api/sessions/{session_id}/catalog", tags=["Catalog"])


@router.get("/{contact_id}")
async def get_catalog(
    session_id: int, contact_id: str, api_key: str = Depends(verify_api_key)
):
    try:
        products = await rpc_call(
            "GET_CATALOG", {"session_id": session_id, "contact_id": contact_id}
        )
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
