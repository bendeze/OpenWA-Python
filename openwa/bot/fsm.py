"""
Finite State Machine (FSM) implementation for OpenWA Bot Framework.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, Optional, Tuple, Type


class State:
    """Represents a state in a conversation flow."""

    def __init__(self, name: Optional[str] = None, group: Optional[str] = None) -> None:
        """Initialize a conversation state.

        Args:
            name: Optional name of the state.
            group: Optional name of the states group container.
        """
        self._name = name
        self._group = group

    @property
    def name(self) -> str:
        """Get the full qualified state name (e.g. GroupName:state_name)."""
        if self._group and self._name:
            return f"{self._group}:{self._name}"
        return self._name or "State"

    def __repr__(self) -> str:
        """Return developer representation of State."""
        return f"<State '{self.name}'>"

    def __str__(self) -> str:
        """Return state name string."""
        return self.name

    def __eq__(self, other: Any) -> bool:
        """Check equality against another State or state name string."""
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
        """Construct new StatesGroup class and tag its State attributes."""
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
        """Retrieve current state string for a given storage key.

        Args:
            key: Tuple of (session_id, chat_id, sender_id).

        Returns:
            Current state name string, or None if in default state.
        """
        pass

    @abc.abstractmethod
    async def set_state(self, key: StorageKey, state: Optional[State | str]) -> None:
        """Set state for a given storage key.

        Args:
            key: Tuple of (session_id, chat_id, sender_id).
            state: State instance or state name string to set, or None to reset.
        """
        pass

    @abc.abstractmethod
    async def clear_state(self, key: StorageKey) -> None:
        """Clear state for a given storage key.

        Args:
            key: Tuple of (session_id, chat_id, sender_id).
        """
        pass

    @abc.abstractmethod
    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        """Retrieve context data dictionary for a given storage key.

        Args:
            key: Tuple of (session_id, chat_id, sender_id).

        Returns:
            Dictionary containing stored user conversation data.
        """
        pass

    @abc.abstractmethod
    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        """Set context data dictionary for a given storage key.

        Args:
            key: Tuple of (session_id, chat_id, sender_id).
            data: Data dictionary to persist.
        """
        pass

    @abc.abstractmethod
    async def update_data(self, key: StorageKey, **kwargs: Any) -> Dict[str, Any]:
        """Update context data with key-value pairs.

        Args:
            key: Tuple of (session_id, chat_id, sender_id).
            **kwargs: Key-value attributes to merge into data.

        Returns:
            Updated context data dictionary.
        """
        pass

    @abc.abstractmethod
    async def clear_data(self, key: StorageKey) -> None:
        """Clear all context data for a given storage key.

        Args:
            key: Tuple of (session_id, chat_id, sender_id).
        """
        pass


class MemoryStorage(BaseStorage):
    """In-memory storage for conversation states and data."""

    def __init__(self) -> None:
        """Initialize empty in-memory state and data dictionaries."""
        self._states: Dict[StorageKey, Optional[str]] = {}
        self._data: Dict[StorageKey, Dict[str, Any]] = {}

    async def get_state(self, key: StorageKey) -> Optional[str]:
        """Retrieve current state string from in-memory dictionary."""
        return self._states.get(key)

    async def set_state(self, key: StorageKey, state: Optional[State | str]) -> None:
        """Set state in in-memory dictionary."""
        if state is None:
            self._states.pop(key, None)
        else:
            self._states[key] = str(state)

    async def clear_state(self, key: StorageKey) -> None:
        """Remove state entry from in-memory dictionary."""
        self._states.pop(key, None)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        """Retrieve copy of context data from in-memory dictionary."""
        return dict(self._data.get(key, {}))

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        """Set context data in in-memory dictionary."""
        self._data[key] = dict(data)

    async def update_data(self, key: StorageKey, **kwargs: Any) -> Dict[str, Any]:
        """Update context data in in-memory dictionary."""
        current = self._data.setdefault(key, {})
        current.update(kwargs)
        return dict(current)

    async def clear_data(self, key: StorageKey) -> None:
        """Remove context data entry from in-memory dictionary."""
        self._data.pop(key, None)
