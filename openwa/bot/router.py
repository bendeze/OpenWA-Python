"""
Router and handler dispatching mechanism for OpenWA Bot Framework.
"""

from __future__ import annotations

import inspect
import re
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Pattern,
    Sequence,
    Union,
)

from openwa.bot.context import Context
from openwa.bot.fsm import State
from openwa.bot.types import EventType, MediaType

HandlerFunc = Callable[[Context], Coroutine[Any, Any, Any]]
FilterFunc = Callable[[Context], Union[bool, Coroutine[Any, Any, bool]]]


class HandlerRegistration:
    """Stores a registered handler function along with its match criteria."""

    def __init__(
        self,
        func: HandlerFunc,
        event_types: Optional[List[EventType]] = None,
        commands: Optional[List[str]] = None,
        prefixes: Optional[Sequence[str]] = None,
        pattern: Optional[Pattern[str]] = None,
        media_types: Optional[List[MediaType]] = None,
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        is_group: Optional[bool] = None,
        custom_filters: Optional[List[FilterFunc]] = None,
    ) -> None:
        self.func = func
        self.event_types = event_types or []
        self.commands = [c.lower() for c in (commands or [])]
        self.prefixes = prefixes or ("/", "!", "#", ".")
        self.pattern = pattern
        self.media_types = media_types or []
        self.state = state
        self.is_group = is_group
        self.custom_filters = custom_filters or []

    async def matches(self, ctx: Context) -> bool:
        """Check if incoming Context satisfies all conditions for this handler."""
        # 1. Event Type Check
        if self.event_types and ctx.event.event not in self.event_types:
            return False

        # 2. State Check
        if self.state is not None:
            current_state = await ctx.get_state()
            allowed_states = (
                [self.state] if not isinstance(self.state, list) else self.state
            )
            allowed_str_states = [str(s) for s in allowed_states]
            if current_state not in allowed_str_states:
                return False

        # 3. Group / DM Filter
        if self.is_group is not None and ctx.message:
            if ctx.message.is_group != self.is_group:
                return False

        # 4. Command Check
        if self.commands:
            if not ctx.text:
                return False
            stripped = ctx.text.strip()
            matched_prefix = None
            for p in self.prefixes:
                if stripped.startswith(p):
                    matched_prefix = p
                    break
            if not matched_prefix:
                return False

            cmd_name = stripped[len(matched_prefix) :].split(maxsplit=1)[0].lower()
            if cmd_name not in self.commands:
                return False

        # 5. Regex Pattern Check
        if self.pattern:
            if not ctx.text or not self.pattern.search(ctx.text):
                return False

        # 6. Media Type Check
        if self.media_types:
            if not ctx.message or not ctx.message.has_media:
                return False
            if ctx.message.media_type not in self.media_types:
                return False

        # 7. Custom Filters
        for f in self.custom_filters:
            res = f(ctx)
            if inspect.isawaitable(res):
                res = await res
            if not res:
                return False

        return True


class Router:
    """Manages routing of incoming events to registered handler callbacks."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name or "root"
        self.handlers: List[HandlerRegistration] = []
        self.sub_routers: List[Router] = []

    def include_router(self, router: Router) -> None:
        """Attach a sub-router."""
        self.sub_routers.append(router)

    def on_command(
        self,
        command: Union[str, Sequence[str]],
        prefixes: Sequence[str] = ("/", "!", "#", "."),
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        is_group: Optional[bool] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Decorator for command messages (e.g. /start, !help)."""
        cmds = [command] if isinstance(command, str) else list(command)

        def decorator(func: HandlerFunc) -> HandlerFunc:
            reg = HandlerRegistration(
                func=func,
                event_types=[EventType.MESSAGE, EventType.MESSAGE_CREATE],
                commands=cmds,
                prefixes=prefixes,
                state=state,
                is_group=is_group,
                custom_filters=filters,
            )
            self.handlers.append(reg)
            return func

        return decorator

    def on_message(
        self,
        pattern: Optional[Union[str, Pattern[str]]] = None,
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        is_group: Optional[bool] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Decorator for general text messages."""
        compiled_pattern = (
            re.compile(pattern) if isinstance(pattern, str) else pattern
        )

        def decorator(func: HandlerFunc) -> HandlerFunc:
            reg = HandlerRegistration(
                func=func,
                event_types=[EventType.MESSAGE, EventType.MESSAGE_CREATE],
                pattern=compiled_pattern,
                state=state,
                is_group=is_group,
                custom_filters=filters,
            )
            self.handlers.append(reg)
            return func

        return decorator

    def on_media(
        self,
        media_type: Optional[Union[MediaType, Sequence[MediaType]]] = None,
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        is_group: Optional[bool] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Decorator for media messages (images, audio, documents, voice notes)."""
        m_types: List[MediaType] = []
        if isinstance(media_type, (MediaType, str)):
            m_types = [MediaType(media_type)]
        elif media_type is not None:
            m_types = [MediaType(m) for m in media_type]

        def decorator(func: HandlerFunc) -> HandlerFunc:
            reg = HandlerRegistration(
                func=func,
                event_types=[EventType.MESSAGE, EventType.MESSAGE_CREATE],
                media_types=m_types,
                state=state,
                is_group=is_group,
                custom_filters=filters,
            )
            self.handlers.append(reg)
            return func

        return decorator

    def on_reaction(
        self,
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Decorator for message reaction events."""

        def decorator(func: HandlerFunc) -> HandlerFunc:
            reg = HandlerRegistration(
                func=func,
                event_types=[EventType.MESSAGE_REACTION],
                state=state,
                custom_filters=filters,
            )
            self.handlers.append(reg)
            return func

        return decorator

    def on_event(
        self,
        event_type: Union[EventType, str],
        state: Optional[Union[State, str, List[Union[State, str]]]] = None,
        filters: Optional[List[FilterFunc]] = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Decorator for arbitrary WhatsApp system events (e.g. qr, session_status)."""
        ev_type = EventType(event_type)

        def decorator(func: HandlerFunc) -> HandlerFunc:
            reg = HandlerRegistration(
                func=func,
                event_types=[ev_type],
                state=state,
                custom_filters=filters,
            )
            self.handlers.append(reg)
            return func

        return decorator

    async def dispatch(self, ctx: Context) -> bool:
        """Dispatch context to matching handler in this router or sub-routers."""
        # 1. Check direct handlers
        for handler in self.handlers:
            if await handler.matches(ctx):
                await handler.func(ctx)
                return True

        # 2. Check sub-routers
        for sub_router in self.sub_routers:
            if await sub_router.dispatch(ctx):
                return True

        return False
