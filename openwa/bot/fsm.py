"""
Finite State Machine (FSM) implementation for OpenWA Bot Framework.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, Optional, Tuple, Type


class State:
    """Represents a state in a conversation flow."""

    def __init__(self, name: Optional[str] = None, group: Optional[str] = None) -> None:
        self._name = name
        self._group = group

    @property
    def name(self) -> str:
        if self._group and self._name:
            return f"{self._group}:{self._name}"
        return self._name or "State"

    def __repr__(self) -> str:
        return f"<State '{self.name}'>"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, State):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False


class StatesGroupMeta(type):
    """Metaclass to automatically attach names and group to State instances."""

    def __new__(
        mcs: Type[StatesGroupMeta],
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
    ) -> StatesGroupMeta:
        cls = super().__new__(mcs, name, bases, namespace)
        for attr_name, value in namespace.items():
            if isinstance(value, State):
                value._name = attr_name
                value._group = name
        return cls


class StatesGroup(metaclass=StatesGroupMeta):
    """Base class for grouping conversation states."""

    pass


# State Storage Key: (session_id, chat_id, sender_id)
StorageKey = Tuple[str, str, str]


class BaseStorage(abc.ABC):
    """Abstract base class for FSM state and data persistence."""

    @abc.abstractmethod
    async def get_state(self, key: StorageKey) -> Optional[str]:
        """Retrieve current state string for a given key."""
        pass

    @abc.abstractmethod
    async def set_state(self, key: StorageKey, state: Optional[State | str]) -> None:
        """Set state for a given key."""
        pass

    @abc.abstractmethod
    async def clear_state(self, key: StorageKey) -> None:
        """Clear state for a given key."""
        pass

    @abc.abstractmethod
    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        """Retrieve context data for a given key."""
        pass

    @abc.abstractmethod
    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        """Set context data for a given key."""
        pass

    @abc.abstractmethod
    async def update_data(self, key: StorageKey, **kwargs: Any) -> Dict[str, Any]:
        """Update context data with key-value pairs."""
        pass

    @abc.abstractmethod
    async def clear_data(self, key: StorageKey) -> None:
        """Clear all context data for a given key."""
        pass


class MemoryStorage(BaseStorage):
    """In-memory storage for conversation states and data."""

    def __init__(self) -> None:
        self._states: Dict[StorageKey, Optional[str]] = {}
        self._data: Dict[StorageKey, Dict[str, Any]] = {}

    async def get_state(self, key: StorageKey) -> Optional[str]:
        return self._states.get(key)

    async def set_state(self, key: StorageKey, state: Optional[State | str]) -> None:
        if state is None:
            self._states.pop(key, None)
        else:
            self._states[key] = str(state)

    async def clear_state(self, key: StorageKey) -> None:
        self._states.pop(key, None)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        return dict(self._data.get(key, {}))

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        self._data[key] = dict(data)

    async def update_data(self, key: StorageKey, **kwargs: Any) -> Dict[str, Any]:
        current = self._data.setdefault(key, {})
        current.update(kwargs)
        return dict(current)

    async def clear_data(self, key: StorageKey) -> None:
        self._data.pop(key, None)
