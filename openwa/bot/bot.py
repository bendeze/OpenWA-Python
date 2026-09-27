"""
Main OpenWABot class combining Client, Router, and FSM Storage.
"""

from __future__ import annotations

import os
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Pattern,
    Sequence,
    Union,
)

from openwa import AsyncOpenWAClient
from openwa.bot.context import Context
from openwa.bot.fsm import BaseStorage, MemoryStorage, State
from openwa.bot.router import FilterFunc, HandlerFunc, Router
from openwa.bot.types import (
    EventPayload,
    EventType,
    MediaType,
    MessagePayload,
    SenderInfo,
)


class OpenWABot:
    """High-level WhatsApp Bot Framework instance."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        storage: Optional[BaseStorage] = None,
        client: Optional[AsyncOpenWAClient] = None,
    ) -> None:
        self.client = client or AsyncOpenWAClient(
            base_url=base_url or os.getenv("OPENWA_BASE_URL"),
            api_key=api_key or os.getenv("OPENWA_API_KEY"),
            timeout=timeout,
        )
        self.storage: BaseStorage = storage or MemoryStorage()
        self.router = Router(name="main_bot_router")

    # -------------------------------------------------------------------------
    # Decorator Proxies
    # -------------------------------------------------------------------------

    def on_command(
        self,
        command: Union[str, Sequence[str]],
        prefixes: Sequence[str] = ("/", "!", "#", "."),
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        is_group: Optional[bool] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a command handler (e.g. /start, !help)."""
        return self.router.on_command(
            command=command,
            prefixes=prefixes,
            state=state,
            is_group=is_group,
            filters=filters,
        )

    def on_message(
        self,
        pattern: Optional[Union[str, Pattern[str]]] = None,
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        is_group: Optional[bool] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a message handler."""
        return self.router.on_message(
            pattern=pattern,
            state=state,
            is_group=is_group,
            filters=filters,
        )

    def on_media(
        self,
        media_type: Optional[Union[MediaType, Sequence[MediaType]]] = None,
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        is_group: Optional[bool] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a media message handler."""
        return self.router.on_media(
            media_type=media_type,
            state=state,
            is_group=is_group,
            filters=filters,
        )

    def on_reaction(
        self,
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register a message reaction handler."""
        return self.router.on_reaction(state=state, filters=filters)

    def on_event(
        self,
        event_type: Union[EventType, str],
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Register an arbitrary WhatsApp system event handler."""
        return self.router.on_event(
            event_type=event_type,
            state=state,
            filters=filters,
        )

    def include_router(self, router: Router) -> None:
        """Attach a sub-router module to this bot."""
        self.router.include_router(router)

    # -------------------------------------------------------------------------
    # Event Normalization & Dispatching
    # -------------------------------------------------------------------------

    def parse_raw_event(self, raw_data: Dict[str, Any]) -> EventPayload:
        """Parse arbitrary OpenWA webhook payload into a normalized EventPayload."""
        event_str = (
            raw_data.get("event")
            or raw_data.get("type")
            or raw_data.get("event_type")
            or "unknown"
        )
        session_id = (
            raw_data.get("session")
            or raw_data.get("sessionId")
            or raw_data.get("session_id")
            or "default"
        )
        data = (
            raw_data.get("data")
            or raw_data.get("payload")
            or raw_data
        )

        try:
            event_type = EventType(event_str)
        except ValueError:
            event_type = EventType.UNKNOWN

        msg_payload: Optional[MessagePayload] = None
        if event_type in (
            EventType.MESSAGE,
            EventType.MESSAGE_CREATE,
            EventType.UNKNOWN,
        ) and isinstance(data, dict):
            # Check if this data dictionary looks like a WhatsApp message
            msg_id = (
                data.get("id")
                or (data.get("_data", {}).get("id", {}).get("_serialized"))
                or ""
            )
            chat_id = (
                data.get("from")
                or data.get("chatId")
                or data.get("to")
                or ""
            )
            if msg_id or chat_id:
                sender_id = (
                    data.get("author")
                    or data.get("from")
                    or chat_id
                )
                sender_name = (
                    data.get("_data", {}).get("notifyName")
                    or data.get("senderName")
                    or data.get("pushname")
                )
                sender = SenderInfo(id=sender_id, name=sender_name)

                body = (
                    data.get("body")
                    or data.get("text")
                    or data.get("caption")
                )
                has_media = bool(
                    data.get("hasMedia")
                    or data.get("mediaUrl")
                    or data.get("mimetype")
                )

                media_type = MediaType.NONE
                raw_type = str(data.get("type", "")).lower()
                if raw_type in ("image", "ptt", "audio", "video", "document", "sticker", "location", "poll"):
                    if raw_type == "ptt":
                        media_type = MediaType.VOICE
                    else:
                        try:
                            media_type = MediaType(raw_type)
                        except ValueError:
                            media_type = MediaType.NONE

                is_group = bool(
                    data.get("isGroup")
                    or str(chat_id).endswith("@g.us")
                )
                is_from_me = bool(
                    data.get("fromMe")
                    or data.get("isFromMe")
                )

                msg_payload = MessagePayload(
                    id=str(msg_id),
                    session_id=str(session_id),
                    chat_id=str(chat_id),
                    sender=sender,
                    text=body,
                    timestamp=int(data.get("timestamp") or 0),
                    is_group=is_group,
                    is_from_me=is_from_me,
                    has_media=has_media,
                    media_type=media_type,
                    media_url=data.get("mediaUrl"),
                    mimetype=data.get("mimetype"),
                    filename=data.get("filename"),
                    quoted_message_id=data.get("quotedMsgId"),
                    raw=data,
                )

        return EventPayload(
            event=event_type,
            session_id=str(session_id),
            data=data if isinstance(data, dict) else {},
            message=msg_payload,
        )

    async def feed_event(self, event: EventPayload) -> bool:
        """Feed a normalized EventPayload to the bot router."""
        ctx = Context(event=event, client=self.client, storage=self.storage)
        return await self.router.dispatch(ctx)

    async def feed_raw_event(self, raw_data: Dict[str, Any]) -> bool:
        """Feed a raw JSON webhook payload directly to the bot."""
        event = self.parse_raw_event(raw_data)
        return await self.feed_event(event)
