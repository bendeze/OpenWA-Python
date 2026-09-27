"""
Context object passed to bot event and message handlers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from openwa.bot.types import EventPayload, MessagePayload
from openwa.bot.fsm import BaseStorage, State, StorageKey

if TYPE_CHECKING:
    from openwa import AsyncOpenWAClient


class Context:
    """Rich execution context for bot handlers."""

    def __init__(
        self,
        event: EventPayload,
        client: AsyncOpenWAClient,
        storage: BaseStorage,
    ) -> None:
        self.event = event
        self.client = client
        self.storage = storage

    @property
    def message(self) -> Optional[MessagePayload]:
        """Get the message payload if this event contains one."""
        return self.event.message

    @property
    def session_id(self) -> str:
        """Get current session ID."""
        return self.event.session_id

    @property
    def chat_id(self) -> str:
        """Get chat ID from message, or empty string."""
        return self.message.chat_id if self.message else ""

    @property
    def sender_id(self) -> str:
        """Get sender ID from message, or empty string."""
        return self.message.sender.id if self.message else ""

    @property
    def text(self) -> Optional[str]:
        """Get message text if available."""
        return self.message.text if self.message else None

    @property
    def command(self) -> Optional[str]:
        """Get command name if available."""
        return self.message.command if self.message else None

    @property
    def command_args(self) -> str:
        """Get command arguments string if available."""
        return self.message.command_args if self.message else ""

    @property
    def storage_key(self) -> StorageKey:
        """Generate unique storage key for FSM state and data."""
        return (self.session_id, self.chat_id, self.sender_id)

    # -------------------------------------------------------------------------
    # Outbound Actions (Replies & Reactions)
    # -------------------------------------------------------------------------

    async def reply(self, text: str) -> Any:
        """Send a text reply to the current chat."""
        if not self.chat_id:
            raise ValueError("Cannot reply: chat_id is missing.")
        return await self.client.messages.send_text(
            self.session_id,
            {"chatId": self.chat_id, "text": text},
        )

    async def reply_image(
        self,
        file: str,
        caption: Optional[str] = None,
    ) -> Any:
        """Send an image to the current chat."""
        if not self.chat_id:
            raise ValueError("Cannot reply: chat_id is missing.")
        data: Dict[str, Any] = {"chatId": self.chat_id, "file": file}
        if caption:
            data["caption"] = caption
        return await self.client.messages.send_image(self.session_id, data)

    async def reply_file(
        self,
        file: str,
        caption: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Any:
        """Send a document or file to the current chat."""
        if not self.chat_id:
            raise ValueError("Cannot reply: chat_id is missing.")
        data: Dict[str, Any] = {"chatId": self.chat_id, "file": file}
        if caption:
            data["caption"] = caption
        if filename:
            data["filename"] = filename
        return await self.client.messages.send_file(self.session_id, data)

    async def reply_location(
        self,
        latitude: float,
        longitude: float,
        title: Optional[str] = None,
    ) -> Any:
        """Send a location to the current chat."""
        if not self.chat_id:
            raise ValueError("Cannot reply: chat_id is missing.")
        data: Dict[str, Any] = {
            "chatId": self.chat_id,
            "latitude": latitude,
            "longitude": longitude,
        }
        if title:
            data["title"] = title
        return await self.client.messages.send_location(self.session_id, data)

    async def reply_poll(
        self,
        name: str,
        options: List[str],
        selectable_count: int = 1,
    ) -> Any:
        """Send a poll to the current chat."""
        if not self.chat_id:
            raise ValueError("Cannot reply: chat_id is missing.")
        data: Dict[str, Any] = {
            "chatId": self.chat_id,
            "name": name,
            "options": options,
            "selectableCount": selectable_count,
        }
        return await self.client.messages.send_poll(self.session_id, data)

    async def react(self, emoji: str) -> Any:
        """React to the current message with an emoji."""
        if not self.message or not self.message.id:
            raise ValueError("Cannot react: message_id is missing.")
        return await self.client.messages.send_reaction(
            self.session_id,
            {
                "chatId": self.chat_id,
                "messageId": self.message.id,
                "reaction": emoji,
            },
        )

    async def quote(self, text: str) -> Any:
        """Reply quoting the current message."""
        if not self.message or not self.message.id:
            raise ValueError("Cannot quote: message_id is missing.")
        return await self.client.messages.reply(
            self.session_id,
            {
                "chatId": self.chat_id,
                "messageId": self.message.id,
                "text": text,
            },
        )

    # -------------------------------------------------------------------------
    # FSM State & Context Data
    # -------------------------------------------------------------------------

    async def get_state(self) -> Optional[str]:
        """Get the current conversation state for this user/chat."""
        return await self.storage.get_state(self.storage_key)

    async def set_state(self, state: Optional[State | str]) -> None:
        """Set a new conversation state for this user/chat."""
        await self.storage.set_state(self.storage_key, state)

    async def clear_state(self) -> None:
        """Clear conversation state."""
        await self.storage.clear_state(self.storage_key)

    async def get_data(self) -> Dict[str, Any]:
        """Get stored context data for this user/chat."""
        return await self.storage.get_data(self.storage_key)

    async def set_data(self, data: Dict[str, Any]) -> None:
        """Set stored context data for this user/chat."""
        await self.storage.set_data(self.storage_key, data)

    async def update_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Update stored context data with key-value pairs."""
        return await self.storage.update_data(self.storage_key, **kwargs)

    async def clear_data(self) -> None:
        """Clear all stored context data for this user/chat."""
        await self.storage.clear_data(self.storage_key)
