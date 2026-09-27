"""
Event and message types for OpenWA Bot Framework.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """WhatsApp event types dispatched by OpenWA."""

    MESSAGE = "message"
    MESSAGE_CREATE = "message_create"
    MESSAGE_REACTION = "message_reaction"
    MESSAGE_REVOKE = "message_revoke"
    MESSAGE_ACK = "message_ack"
    QR = "qr"
    SESSION_STATUS = "session_status"
    GROUP_JOIN = "group_join"
    GROUP_LEAVE = "group_leave"
    UNKNOWN = "unknown"


class MediaType(str, Enum):
    """Supported media types."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    DOCUMENT = "document"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACT = "contact"
    POLL = "poll"
    NONE = "none"


class SenderInfo(BaseModel):
    """Information about the sender of a message."""

    id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    is_business: bool = False


class MessagePayload(BaseModel):
    """Normalized WhatsApp incoming message payload."""

    id: str
    session_id: str
    chat_id: str
    sender: SenderInfo
    text: Optional[str] = None
    timestamp: int = 0
    is_group: bool = False
    is_from_me: bool = False
    has_media: bool = False
    media_type: MediaType = MediaType.NONE
    media_url: Optional[str] = None
    mimetype: Optional[str] = None
    filename: Optional[str] = None
    quoted_message_id: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)

    @property
    def command(self) -> Optional[str]:
        """Extract the command string if message starts with / or !."""
        if not self.text:
            return None
        stripped = self.text.strip()
        if stripped.startswith(("/", "!", "#", ".")):
            parts = stripped.split(maxsplit=1)
            return parts[0]
        return None

    @property
    def command_args(self) -> str:
        """Extract the arguments passed after a command."""
        if not self.text:
            return ""
        stripped = self.text.strip()
        if stripped.startswith(("/", "!", "#", ".")):
            parts = stripped.split(maxsplit=1)
            return parts[1] if len(parts) > 1 else ""
        return ""


class EventPayload(BaseModel):
    """Normalized incoming webhook event wrapper."""

    event: EventType = EventType.UNKNOWN
    session_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[MessagePayload] = None
