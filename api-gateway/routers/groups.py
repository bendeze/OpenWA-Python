import schemas
from dependencies import verify_api_key
from fastapi import APIRouter, Depends, HTTPException
from redis_client import rpc_call

router = APIRouter(prefix="/api/sessions/{session_id}/groups", tags=["Group"])


@router.get("")
async def get_groups(session_id: int, api_key: str = Depends(verify_api_key)):
    try:
        groups = await rpc_call("GET_GROUPS", {"session_id": session_id})
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateGroupDto(schemas.BaseModel):
    name: str
    participants: list[str]


@router.post("")
async def create_group(
    session_id: int, dto: CreateGroupDto, api_key: str = Depends(verify_api_key)
):
    try:
        result = await rpc_call(
            "CREATE_GROUP",
            {
                "session_id": session_id,
                "name": dto.name,
                "participants": dto.participants,
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ParticipantsDto(schemas.BaseModel):
    participants: list[str]


@router.post("/{group_id}/participants")
async def add_participants(
    session_id: int,
    group_id: str,
    dto: ParticipantsDto,
    api_key: str = Depends(verify_api_key),
):
    try:
        result = await rpc_call(
            "ADD_PARTICIPANTS",
            {
                "session_id": session_id,
                "group_id": group_id,
                "participants": dto.participants,
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{group_id}/participants")
async def remove_participants(
    session_id: int,
    group_id: str,
    dto: ParticipantsDto,
    api_key: str = Depends(verify_api_key),
):
    try:
        result = await rpc_call(
            "REMOVE_PARTICIPANTS",
            {
                "session_id": session_id,
                "group_id": group_id,
                "participants": dto.participants,
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GroupSubjectDto(schemas.BaseModel):
    subject: str


@router.put("/{group_id}/subject")
async def set_subject(
    session_id: int,
    group_id: str,
    dto: GroupSubjectDto,
    api_key: str = Depends(verify_api_key),
):
    try:
        result = await rpc_call(
            "SET_GROUP_SUBJECT",
            {"session_id": session_id, "group_id": group_id, "subject": dto.subject},
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
