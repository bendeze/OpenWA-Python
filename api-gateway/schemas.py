from typing import List, Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    name: str


class MessageCreate(BaseModel):
    chatId: str
    text: str


class MessageMedia(BaseModel):
    chatId: str
    url: str
    caption: Optional[str] = None
    filename: Optional[str] = None


class WebhookCreate(BaseModel):
    url: str
    events: List[str]
    secret: str


class SessionResponse(BaseModel):
    id: str
    name: str
    status: str

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    name: str
    role: str


class ApiKeyUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    keyPrefix: str
    role: str
    isActive: bool
    lastUsedAt: Optional[str] = None
    createdAt: str
    apiKey: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    url: str
    events: List[str]
    secret: str
    createdAt: str


class SaveConfigPayload(BaseModel):
    database: dict
    redis: dict
    queue: dict
    storage: dict
    server: dict
    webhook: dict
    rateLimit: dict


class RestartPayload(BaseModel):
    profiles: List[str] = []
    profilesToRemove: List[str] = []


class ChatUnreadRequest(BaseModel):
    chatId: str
