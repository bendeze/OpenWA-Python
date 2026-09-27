"""
OpenWA Python SDK

Official client library and bot framework for the OpenWA WhatsApp API Gateway.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional


class OpenWAError(Exception):
    """Base exception for OpenWA SDK."""


class OpenWAAPIError(OpenWAError):
    """API returned an error response."""

    def __init__(self, status_code: int, message: str) -> None:
        """Initialize OpenWAAPIError with status code and detail message."""
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


@dataclass
class OpenWAClientConfig:
    """Configuration for the OpenWA client.

    Attributes:
        base_url: Base URL of the OpenWA engine instance.
        api_key: API key used for authentication.
        timeout: HTTP request timeout in seconds.
    """

    base_url: str
    api_key: str
    timeout: float = 30.0


@dataclass
class MessageResponse:
    """Standard response returned after sending a message.

    Attributes:
        message_id: Unique WhatsApp message identifier.
        timestamp: Epoch timestamp when the message was processed.
    """

    message_id: str
    timestamp: int


class _BaseClient:
    """Internal base client managing shared configuration and response handling."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """Initialize base client configuration."""
        url = base_url or os.getenv("OPENWA_BASE_URL")
        key = api_key or os.getenv("OPENWA_API_KEY")
        if not url:
            raise ValueError(
                "base_url must be provided or set via OPENWA_BASE_URL environment variable."
            )
        if not key:
            raise ValueError(
                "api_key must be provided or set via OPENWA_API_KEY environment variable."
            )

        self.config = OpenWAClientConfig(
            base_url=url.rstrip("/"),
            api_key=key,
            timeout=timeout,
        )

    def _handle_response(self, response: Any) -> Any:
        """Handle HTTP response and raise OpenWAAPIError on non-2xx status codes."""
        if 400 <= response.status_code < 600:
            try:
                error_data = response.json()
                msg = (
                    error_data.get("detail")
                    or error_data.get("message")
                    or response.text
                )
            except Exception:
                msg = response.text
            raise OpenWAAPIError(response.status_code, msg)

        if response.status_code == 204:
            return None
        return response.json()


class OpenWAClient(_BaseClient):
    """Synchronous OpenWA API client."""

    @property
    def sessions(self) -> "_SessionsResource":
        """Access session management resource."""
        return _SessionsResource(self)

    @property
    def messages(self) -> "_MessagesResource":
        """Access messaging resource."""
        return _MessagesResource(self)

    @property
    def webhooks(self) -> "_WebhooksResource":
        """Access webhook management resource."""
        return _WebhooksResource(self)

    @property
    def api_keys(self) -> "_ApiKeysResource":
        """Access API key management resource."""
        return _ApiKeysResource(self)

    @property
    def contacts(self) -> "_ContactsResource":
        """Access contacts resource."""
        return _ContactsResource(self)

    @property
    def groups(self) -> "_GroupsResource":
        """Access groups resource."""
        return _GroupsResource(self)

    def _request(self, method: str, path: str, json: Any = None) -> Any:
        """Execute a synchronous HTTP request against the OpenWA gateway."""
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required. Install with: pip install httpx")

        with httpx.Client(timeout=self.config.timeout) as client:
            request_kwargs = {"json": json} if json is not None else {}
            if method == "DELETE" and json is not None:
                request_kwargs = {
                    "request": client.build_request(
                        "DELETE",
                        f"{self.config.base_url}{path}",
                        json=json,
                        headers={
                            "Content-Type": "application/json",
                            "X-API-Key": self.config.api_key,
                        },
                    )
                }
                response = client.send(request_kwargs["request"])
            else:
                response = client.request(
                    method,
                    f"{self.config.base_url}{path}",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.config.api_key,
                    },
                    **request_kwargs,
                )
            return self._handle_response(response)


class AsyncOpenWAClient(_BaseClient):
    """Asynchronous OpenWA API client."""

    async def __aenter__(self) -> "AsyncOpenWAClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        pass

    @property
    def sessions(self) -> "_AsyncSessionsResource":
        """Access async session management resource."""
        return _AsyncSessionsResource(self)

    @property
    def messages(self) -> "_AsyncMessagesResource":
        """Access async messaging resource."""
        return _AsyncMessagesResource(self)

    @property
    def webhooks(self) -> "_AsyncWebhooksResource":
        """Access async webhook management resource."""
        return _AsyncWebhooksResource(self)

    @property
    def api_keys(self) -> "_AsyncApiKeysResource":
        """Access async API key management resource."""
        return _AsyncApiKeysResource(self)

    @property
    def contacts(self) -> "_AsyncContactsResource":
        """Access async contacts resource."""
        return _AsyncContactsResource(self)

    @property
    def groups(self) -> "_AsyncGroupsResource":
        """Access async groups resource."""
        return _AsyncGroupsResource(self)

    async def _request(self, method: str, path: str, json: Any = None) -> Any:
        """Execute an asynchronous HTTP request against the OpenWA gateway."""
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required. Install with: pip install httpx")

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            request_kwargs = {"json": json} if json is not None else {}
            if method == "DELETE" and json is not None:
                req = client.build_request(
                    "DELETE",
                    f"{self.config.base_url}{path}",
                    json=json,
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.config.api_key,
                    },
                )
                response = await client.send(req)
            else:
                response = await client.request(
                    method,
                    f"{self.config.base_url}{path}",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": self.config.api_key,
                    },
                    **request_kwargs,
                )
            return self._handle_response(response)


class _SessionsResource:
    """Synchronous session management endpoints."""

    def __init__(self, client: OpenWAClient) -> None:
        """Initialize session resource with parent client."""
        self._client = client

    def list(self) -> list[dict]:
        """List all active WhatsApp sessions."""
        return self._client._request("GET", "/api/sessions")

    def get(self, session_id: str) -> dict:
        """Retrieve metadata for a specific session."""
        return self._client._request("GET", f"/api/sessions/{session_id}")

    def create(self, name: str) -> dict:
        """Create a new session configuration."""
        return self._client._request("POST", "/api/sessions", {"name": name})

    def start(self, session_id: str) -> dict:
        """Start WhatsApp connection and browser for a session."""
        return self._client._request("POST", f"/api/sessions/{session_id}/start")

    def stop(self, session_id: str) -> dict:
        """Disconnect and stop a session."""
        return self._client._request("POST", f"/api/sessions/{session_id}/stop")

    def delete(self, session_id: str) -> None:
        """Delete session data and authentication tokens."""
        self._client._request("DELETE", f"/api/sessions/{session_id}")

    def qr(self, session_id: str) -> dict:
        """Fetch login QR code image data for a session."""
        return self._client._request("GET", f"/api/sessions/{session_id}/qr")

    def mark_chat_unread(self, session_id: str, chat_id: str) -> dict:
        """Mark a chat as unread."""
        return self._client._request(
            "POST", f"/api/sessions/{session_id}/chats/unread", {"chatId": chat_id}
        )


class _AsyncSessionsResource:
    """Asynchronous session management endpoints."""

    def __init__(self, client: AsyncOpenWAClient) -> None:
        """Initialize async session resource with parent client."""
        self._client = client

    async def list(self) -> list[dict]:
        """List all active WhatsApp sessions asynchronously."""
        return await self._client._request("GET", "/api/sessions")

    async def get(self, session_id: str) -> dict:
        """Retrieve metadata for a specific session asynchronously."""
        return await self._client._request("GET", f"/api/sessions/{session_id}")

    async def create(self, name: str) -> dict:
        """Create a new session configuration asynchronously."""
        return await self._client._request("POST", "/api/sessions", {"name": name})

    async def start(self, session_id: str) -> dict:
        """Start WhatsApp connection and browser asynchronously."""
        return await self._client._request("POST", f"/api/sessions/{session_id}/start")

    async def stop(self, session_id: str) -> dict:
        """Disconnect and stop a session asynchronously."""
        return await self._client._request("POST", f"/api/sessions/{session_id}/stop")

    async def delete(self, session_id: str) -> None:
        """Delete session data and authentication tokens asynchronously."""
        await self._client._request("DELETE", f"/api/sessions/{session_id}")

    async def qr(self, session_id: str) -> dict:
        """Fetch login QR code image data asynchronously."""
        return await self._client._request("GET", f"/api/sessions/{session_id}/qr")

    async def mark_chat_unread(self, session_id: str, chat_id: str) -> dict:
        """Mark a chat as unread asynchronously."""
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/chats/unread", {"chatId": chat_id}
        )


class _MessagesResource:
    """Synchronous messaging endpoints."""

    def __init__(self, client: OpenWAClient) -> None:
        """Initialize messages resource with parent client."""
        self._client = client

    def list(self, session_id: str) -> list[dict]:
        """List messages for a session."""
        return self._client._request("GET", f"/api/sessions/{session_id}/messages")

    def send_text(self, session_id: str, data: dict[str, str]) -> MessageResponse:
        """Send a text message to a chat."""
        res = self._client._request(
            "POST", f"/api/sessions/{session_id}/messages/send-text", data
        )
        msg_id = (
            str(res.get("messageId") or res.get("id") or "")
            if isinstance(res, dict)
            else ""
        )
        ts = int(res.get("timestamp") or 0) if isinstance(res, dict) else 0
        return MessageResponse(msg_id, ts)


class _AsyncMessagesResource:
    """Asynchronous messaging endpoints."""

    def __init__(self, client: AsyncOpenWAClient) -> None:
        """Initialize async messages resource with parent client."""
        self._client = client

    async def list(self, session_id: str) -> list[dict]:
        """List messages for a session asynchronously."""
        return await self._client._request(
            "GET", f"/api/sessions/{session_id}/messages"
        )

    async def send_text(self, session_id: str, data: dict[str, str]) -> MessageResponse:
        """Send a text message to a chat asynchronously."""
        res = await self._client._request(
            "POST", f"/api/sessions/{session_id}/messages/send-text", data
        )
        msg_id = (
            str(res.get("messageId") or res.get("id") or "")
            if isinstance(res, dict)
            else ""
        )
        ts = int(res.get("timestamp") or 0) if isinstance(res, dict) else 0
        return MessageResponse(msg_id, ts)


class _WebhooksResource:
    """Synchronous webhook management endpoints."""

    def __init__(self, client: OpenWAClient) -> None:
        """Initialize webhooks resource with parent client."""
        self._client = client

    def list_all(self) -> list[dict]:
        """List all active webhook configurations."""
        return self._client._request("GET", "/api/webhooks")

    def create(self, session_id: str, data: dict) -> dict:
        """Create a webhook configuration for a session."""
        return self._client._request(
            "POST", f"/api/sessions/{session_id}/webhooks", data
        )

    def update(self, session_id: str, webhook_id: str, data: dict) -> dict:
        """Update an existing webhook configuration."""
        return self._client._request(
            "PUT", f"/api/sessions/{session_id}/webhooks/{webhook_id}", data
        )

    def delete(self, session_id: str, webhook_id: str) -> None:
        """Delete a webhook configuration."""
        self._client._request(
            "DELETE", f"/api/sessions/{session_id}/webhooks/{webhook_id}"
        )


class _AsyncWebhooksResource:
    """Asynchronous webhook management endpoints."""

    def __init__(self, client: AsyncOpenWAClient) -> None:
        """Initialize async webhooks resource with parent client."""
        self._client = client

    async def list_all(self) -> list[dict]:
        """List all active webhook configurations asynchronously."""
        return await self._client._request("GET", "/api/webhooks")

    async def create(self, session_id: str, data: dict) -> dict:
        """Create a webhook configuration for a session asynchronously."""
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/webhooks", data
        )

    async def update(self, session_id: str, webhook_id: str, data: dict) -> dict:
        """Update an existing webhook configuration asynchronously."""
        return await self._client._request(
            "PUT", f"/api/sessions/{session_id}/webhooks/{webhook_id}", data
        )

    async def delete(self, session_id: str, webhook_id: str) -> None:
        """Delete a webhook configuration asynchronously."""
        await self._client._request(
            "DELETE", f"/api/sessions/{session_id}/webhooks/{webhook_id}"
        )


class _ApiKeysResource:
    """Synchronous API key management endpoints."""

    def __init__(self, client: OpenWAClient) -> None:
        """Initialize API keys resource with parent client."""
        self._client = client

    def list(self) -> list[dict]:
        """List active API keys."""
        return self._client._request("GET", "/api/api-keys")

    def create(self, data: dict) -> dict:
        """Create a new API key."""
        return self._client._request("POST", "/api/api-keys", data)

    def delete(self, key_id: str) -> None:
        """Revoke and delete an API key."""
        self._client._request("DELETE", f"/api/api-keys/{key_id}")


class _AsyncApiKeysResource:
    """Asynchronous API key management endpoints."""

    def __init__(self, client: AsyncOpenWAClient) -> None:
        """Initialize async API keys resource with parent client."""
        self._client = client

    async def list(self) -> list[dict]:
        """List active API keys asynchronously."""
        return await self._client._request("GET", "/api/api-keys")

    async def create(self, data: dict) -> dict:
        """Create a new API key asynchronously."""
        return await self._client._request("POST", "/api/api-keys", data)

    async def delete(self, key_id: str) -> None:
        """Revoke and delete an API key asynchronously."""
        await self._client._request("DELETE", f"/api/api-keys/{key_id}")


class _ContactsResource:
    """Synchronous contacts endpoints."""

    def __init__(self, client: OpenWAClient) -> None:
        """Initialize contacts resource with parent client."""
        self._client = client

    def list(self, session_id: str) -> list[dict]:
        """List contacts for a session."""
        return self._client._request("GET", f"/api/sessions/{session_id}/contacts")

    def get(self, session_id: str, contact_id: str) -> dict:
        """Retrieve profile information for a specific contact."""
        return self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts/{contact_id}"
        )

    def block(self, session_id: str, contact_id: str) -> None:
        """Block a contact."""
        self._client._request(
            "POST", f"/api/sessions/{session_id}/contacts/{contact_id}/block"
        )

    def unblock(self, session_id: str, contact_id: str) -> None:
        """Unblock a contact."""
        self._client._request(
            "POST", f"/api/sessions/{session_id}/contacts/{contact_id}/unblock"
        )


class _AsyncContactsResource:
    """Asynchronous contacts endpoints."""

    def __init__(self, client: AsyncOpenWAClient) -> None:
        """Initialize async contacts resource with parent client."""
        self._client = client

    async def list(self, session_id: str) -> list[dict]:
        """List contacts for a session asynchronously."""
        return await self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts"
        )

    async def get(self, session_id: str, contact_id: str) -> dict:
        """Retrieve profile information for a specific contact asynchronously."""
        return await self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts/{contact_id}"
        )

    async def block(self, session_id: str, contact_id: str) -> None:
        """Block a contact asynchronously."""
        await self._client._request(
            "POST", f"/api/sessions/{session_id}/contacts/{contact_id}/block"
        )

    async def unblock(self, session_id: str, contact_id: str) -> None:
        """Unblock a contact asynchronously."""
        await self._client._request(
            "POST", f"/api/sessions/{session_id}/contacts/{contact_id}/unblock"
        )


class _GroupsResource:
    """Synchronous group chat management endpoints."""

    def __init__(self, client: OpenWAClient) -> None:
        """Initialize groups resource with parent client."""
        self._client = client

    def list(self, session_id: str) -> list[dict]:
        """List group chats for a session."""
        return self._client._request("GET", f"/api/sessions/{session_id}/groups")

    def create(self, session_id: str, data: dict) -> dict:
        """Create a new group chat."""
        return self._client._request("POST", f"/api/sessions/{session_id}/groups", data)

    def add_participants(self, session_id: str, group_id: str, data: dict) -> dict:
        """Add participant phone numbers to a group."""
        return self._client._request(
            "POST", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    def remove_participants(self, session_id: str, group_id: str, data: dict) -> dict:
        """Remove participants from a group."""
        return self._client._request(
            "DELETE", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    def set_subject(self, session_id: str, group_id: str, data: dict) -> dict:
        """Update group subject / title."""
        return self._client._request(
            "PUT", f"/api/sessions/{session_id}/groups/{group_id}/subject", data
        )


class _AsyncGroupsResource:
    """Asynchronous group chat management endpoints."""

    def __init__(self, client: AsyncOpenWAClient) -> None:
        """Initialize async groups resource with parent client."""
        self._client = client

    async def list(self, session_id: str) -> list[dict]:
        """List group chats for a session asynchronously."""
        return await self._client._request("GET", f"/api/sessions/{session_id}/groups")

    async def create(self, session_id: str, data: dict) -> dict:
        """Create a new group chat asynchronously."""
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/groups", data
        )

    async def add_participants(
        self, session_id: str, group_id: str, data: dict
    ) -> dict:
        """Add participant phone numbers to a group asynchronously."""
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    async def remove_participants(
        self, session_id: str, group_id: str, data: dict
    ) -> dict:
        """Remove participants from a group asynchronously."""
        return await self._client._request(
            "DELETE", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    async def set_subject(self, session_id: str, group_id: str, data: dict) -> dict:
        """Update group subject / title asynchronously."""
        return await self._client._request(
            "PUT", f"/api/sessions/{session_id}/groups/{group_id}/subject", data
        )


from openwa.bot import (BaseStorage, Context, EventPayload, EventType,
                        MediaType, MemoryStorage, MessagePayload, OpenWABot,
                        Router, SenderInfo, State, StatesGroup)

__all__ = [
    "OpenWAClient",
    "AsyncOpenWAClient",
    "OpenWAError",
    "OpenWAAPIError",
    "OpenWAClientConfig",
    "MessageResponse",
    "OpenWABot",
    "Router",
    "Context",
    "State",
    "StatesGroup",
    "BaseStorage",
    "MemoryStorage",
    "EventPayload",
    "EventType",
    "MediaType",
    "MessagePayload",
    "SenderInfo",
]
