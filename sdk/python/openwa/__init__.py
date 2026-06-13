"""
OpenWA Python SDK

Official client library for the OpenWA WhatsApp API Gateway.
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
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


@dataclass
class OpenWAClientConfig:
    """Configuration for the OpenWA client."""

    base_url: str
    api_key: str
    timeout: float = 30.0


@dataclass
class MessageResponse:
    message_id: str
    timestamp: int


class _BaseClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
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
        return _SessionsResource(self)

    @property
    def messages(self) -> "_MessagesResource":
        return _MessagesResource(self)

    @property
    def webhooks(self) -> "_WebhooksResource":
        return _WebhooksResource(self)

    @property
    def api_keys(self) -> "_ApiKeysResource":
        return _ApiKeysResource(self)

    @property
    def contacts(self) -> "_ContactsResource":
        return _ContactsResource(self)

    @property
    def groups(self) -> "_GroupsResource":
        return _GroupsResource(self)

    def _request(self, method: str, path: str, json: Any = None) -> Any:
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

    @property
    def sessions(self) -> "_AsyncSessionsResource":
        return _AsyncSessionsResource(self)

    @property
    def messages(self) -> "_AsyncMessagesResource":
        return _AsyncMessagesResource(self)

    @property
    def webhooks(self) -> "_AsyncWebhooksResource":
        return _AsyncWebhooksResource(self)

    @property
    def api_keys(self) -> "_AsyncApiKeysResource":
        return _AsyncApiKeysResource(self)

    @property
    def contacts(self) -> "_AsyncContactsResource":
        return _AsyncContactsResource(self)

    @property
    def groups(self) -> "_AsyncGroupsResource":
        return _AsyncGroupsResource(self)

    async def _request(self, method: str, path: str, json: Any = None) -> Any:
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
    def __init__(self, client: OpenWAClient) -> None:
        self._client = client

    def list(self) -> list[dict]:
        return self._client._request("GET", "/api/sessions")

    def get(self, session_id: str) -> dict:
        return self._client._request("GET", f"/api/sessions/{session_id}")

    def create(self, name: str) -> dict:
        return self._client._request("POST", "/api/sessions", {"name": name})

    def start(self, session_id: str) -> dict:
        return self._client._request("POST", f"/api/sessions/{session_id}/start")

    def stop(self, session_id: str) -> dict:
        return self._client._request("POST", f"/api/sessions/{session_id}/stop")

    def delete(self, session_id: str) -> None:
        self._client._request("DELETE", f"/api/sessions/{session_id}")

    def qr(self, session_id: str) -> dict:
        return self._client._request("GET", f"/api/sessions/{session_id}/qr")


class _AsyncSessionsResource:
    def __init__(self, client: AsyncOpenWAClient) -> None:
        self._client = client

    async def list(self) -> list[dict]:
        return await self._client._request("GET", "/api/sessions")

    async def get(self, session_id: str) -> dict:
        return await self._client._request("GET", f"/api/sessions/{session_id}")

    async def create(self, name: str) -> dict:
        return await self._client._request("POST", "/api/sessions", {"name": name})

    async def start(self, session_id: str) -> dict:
        return await self._client._request("POST", f"/api/sessions/{session_id}/start")

    async def stop(self, session_id: str) -> dict:
        return await self._client._request("POST", f"/api/sessions/{session_id}/stop")

    async def delete(self, session_id: str) -> None:
        await self._client._request("DELETE", f"/api/sessions/{session_id}")

    async def qr(self, session_id: str) -> dict:
        return await self._client._request("GET", f"/api/sessions/{session_id}/qr")


class _MessagesResource:
    def __init__(self, client: OpenWAClient) -> None:
        self._client = client

    def list(self, session_id: str) -> list[dict]:
        return self._client._request("GET", f"/api/sessions/{session_id}/messages")

    def send_text(self, session_id: str, data: dict[str, str]) -> MessageResponse:
        res = self._client._request(
            "POST", f"/api/sessions/{session_id}/messages/send-text", data
        )
        return MessageResponse(res["messageId"], res["timestamp"])


class _AsyncMessagesResource:
    def __init__(self, client: AsyncOpenWAClient) -> None:
        self._client = client

    async def list(self, session_id: str) -> list[dict]:
        return await self._client._request(
            "GET", f"/api/sessions/{session_id}/messages"
        )

    async def send_text(self, session_id: str, data: dict[str, str]) -> MessageResponse:
        res = await self._client._request(
            "POST", f"/api/sessions/{session_id}/messages/send-text", data
        )
        return MessageResponse(res["messageId"], res["timestamp"])


class _WebhooksResource:
    def __init__(self, client: OpenWAClient) -> None:
        self._client = client

    def list_all(self) -> list[dict]:
        return self._client._request("GET", "/api/webhooks")

    def create(self, session_id: str, data: dict) -> dict:
        return self._client._request(
            "POST", f"/api/sessions/{session_id}/webhooks", data
        )

    def update(self, session_id: str, webhook_id: str, data: dict) -> dict:
        return self._client._request(
            "PUT", f"/api/sessions/{session_id}/webhooks/{webhook_id}", data
        )

    def delete(self, session_id: str, webhook_id: str) -> None:
        self._client._request(
            "DELETE", f"/api/sessions/{session_id}/webhooks/{webhook_id}"
        )


class _AsyncWebhooksResource:
    def __init__(self, client: AsyncOpenWAClient) -> None:
        self._client = client

    async def list_all(self) -> list[dict]:
        return await self._client._request("GET", "/api/webhooks")

    async def create(self, session_id: str, data: dict) -> dict:
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/webhooks", data
        )

    async def update(self, session_id: str, webhook_id: str, data: dict) -> dict:
        return await self._client._request(
            "PUT", f"/api/sessions/{session_id}/webhooks/{webhook_id}", data
        )

    async def delete(self, session_id: str, webhook_id: str) -> None:
        await self._client._request(
            "DELETE", f"/api/sessions/{session_id}/webhooks/{webhook_id}"
        )


class _ApiKeysResource:
    def __init__(self, client: OpenWAClient) -> None:
        self._client = client

    def list(self) -> list[dict]:
        return self._client._request("GET", "/api/auth/api-keys")

    def create(self, data: dict) -> dict:
        return self._client._request("POST", "/api/auth/api-keys", data)

    def revoke(self, key_id: str) -> dict:
        return self._client._request("POST", f"/api/auth/api-keys/{key_id}/revoke")

    def rotate(self, key_id: str) -> dict:
        return self._client._request("POST", f"/api/auth/api-keys/{key_id}/rotate")

    def delete(self, key_id: str) -> None:
        self._client._request("DELETE", f"/api/auth/api-keys/{key_id}")


class _AsyncApiKeysResource:
    def __init__(self, client: AsyncOpenWAClient) -> None:
        self._client = client

    async def list(self) -> list[dict]:
        return await self._client._request("GET", "/api/auth/api-keys")

    async def create(self, data: dict) -> dict:
        return await self._client._request("POST", "/api/auth/api-keys", data)

    async def revoke(self, key_id: str) -> dict:
        return await self._client._request(
            "POST", f"/api/auth/api-keys/{key_id}/revoke"
        )

    async def rotate(self, key_id: str) -> dict:
        return await self._client._request(
            "POST", f"/api/auth/api-keys/{key_id}/rotate"
        )

    async def delete(self, key_id: str) -> None:
        await self._client._request("DELETE", f"/api/auth/api-keys/{key_id}")


class _ContactsResource:
    def __init__(self, client: OpenWAClient) -> None:
        self._client = client

    def list(self, session_id: str) -> list[dict]:
        return self._client._request("GET", f"/api/sessions/{session_id}/contacts")

    def get(self, session_id: str, contact_id: str) -> dict:
        return self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts/{contact_id}"
        )

    def check_number(self, session_id: str, number: str) -> dict:
        return self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts/check/{number}"
        )

    def block(self, session_id: str, contact_id: str) -> dict:
        return self._client._request(
            "POST", f"/api/sessions/{session_id}/contacts/{contact_id}/block"
        )


class _AsyncContactsResource:
    def __init__(self, client: AsyncOpenWAClient) -> None:
        self._client = client

    async def list(self, session_id: str) -> list[dict]:
        return await self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts"
        )

    async def get(self, session_id: str, contact_id: str) -> dict:
        return await self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts/{contact_id}"
        )

    async def check_number(self, session_id: str, number: str) -> dict:
        return await self._client._request(
            "GET", f"/api/sessions/{session_id}/contacts/check/{number}"
        )

    async def block(self, session_id: str, contact_id: str) -> dict:
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/contacts/{contact_id}/block"
        )


class _GroupsResource:
    def __init__(self, client: OpenWAClient) -> None:
        self._client = client

    def list(self, session_id: str) -> list[dict]:
        return self._client._request("GET", f"/api/sessions/{session_id}/groups")

    def create(self, session_id: str, data: dict) -> dict:
        return self._client._request("POST", f"/api/sessions/{session_id}/groups", data)

    def add_participants(self, session_id: str, group_id: str, data: dict) -> dict:
        return self._client._request(
            "POST", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    def remove_participants(self, session_id: str, group_id: str, data: dict) -> dict:
        return self._client._request(
            "DELETE", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    def set_subject(self, session_id: str, group_id: str, data: dict) -> dict:
        return self._client._request(
            "PUT", f"/api/sessions/{session_id}/groups/{group_id}/subject", data
        )


class _AsyncGroupsResource:
    def __init__(self, client: AsyncOpenWAClient) -> None:
        self._client = client

    async def list(self, session_id: str) -> list[dict]:
        return await self._client._request("GET", f"/api/sessions/{session_id}/groups")

    async def create(self, session_id: str, data: dict) -> dict:
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/groups", data
        )

    async def add_participants(
        self, session_id: str, group_id: str, data: dict
    ) -> dict:
        return await self._client._request(
            "POST", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    async def remove_participants(
        self, session_id: str, group_id: str, data: dict
    ) -> dict:
        return await self._client._request(
            "DELETE", f"/api/sessions/{session_id}/groups/{group_id}/participants", data
        )

    async def set_subject(self, session_id: str, group_id: str, data: dict) -> dict:
        return await self._client._request(
            "PUT", f"/api/sessions/{session_id}/groups/{group_id}/subject", data
        )
