# 03 - SDK Reference

The `openwa` package provides both synchronous (`OpenWAClient`) and asynchronous (`AsyncOpenWAClient`) interfaces.

---

## Client Initialization

```python
from openwa import OpenWAClient, AsyncOpenWAClient

# Explicit configuration:
client = OpenWAClient(base_url="http://localhost:3000", api_key="secret", timeout=30.0)

# Or via environment variables (OPENWA_BASE_URL and OPENWA_API_KEY):
client = OpenWAClient()
```

---

## 1. Sessions (`client.sessions`)

Manage WhatsApp connections, QR codes, and session lifecycles.

| Method | Parameters | Description |
| :--- | :--- | :--- |
| `list()` | - | List all configured sessions |
| `get(session_id)` | `session_id: str` | Get metadata for a specific session |
| `create(name)` | `name: str` | Create a new named session |
| `start(session_id)` | `session_id: str` | Launch session browser / connection |
| `stop(session_id)` | `session_id: str` | Disconnect session |
| `restart(session_id)` | `session_id: str` | Restart session |
| `delete(session_id)` | `session_id: str` | Permanently delete session and tokens |
| `qr(session_id)` | `session_id: str` | Get Base64 QR code image for scanning |
| `status(session_id)` | `session_id: str` | Check current connection status |

---

## 2. Messages (`client.messages`)

Send messages and interactive content to WhatsApp chats.

| Method | Parameters | Description |
| :--- | :--- | :--- |
| `send_text(session_id, data)` | `session_id: str, data: dict` | Send text message (`{"chatId": "...", "text": "..."}`) |
| `send_image(session_id, data)` | `session_id: str, data: dict` | Send image with caption (`{"chatId": "...", "file": "...", "caption": "..."}`) |
| `send_file(session_id, data)` | `session_id: str, data: dict` | Send document / file |
| `send_location(session_id, data)` | `session_id: str, data: dict` | Send GPS coordinates |
| `send_contact(session_id, data)` | `session_id: str, data: dict` | Send vCard contact card |
| `send_poll(session_id, data)` | `session_id: str, data: dict` | Create a WhatsApp poll |
| `send_reaction(session_id, data)` | `session_id: str, data: dict` | React to a message with emoji |
| `reply(session_id, data)` | `session_id: str, data: dict` | Reply to a specific `messageId` |
| `delete(session_id, message_id)` | `session_id: str, message_id: str` | Revoke / delete a sent message |

---

## 3. Webhooks (`client.webhooks`)

Configure URLs where OpenWA pushes incoming message events.

| Method | Parameters | Description |
| :--- | :--- | :--- |
| `list()` | - | List active webhook subscriptions |
| `create(data)` | `data: dict` | Register a new webhook endpoint URL |
| `get(webhook_id)` | `webhook_id: str` | Get webhook details |
| `update(webhook_id, data)` | `webhook_id: str, data: dict` | Update webhook URL or events |
| `delete(webhook_id)` | `webhook_id: str` | Remove webhook subscription |

---

## 4. Contacts (`client.contacts`)

| Method | Parameters | Description |
| :--- | :--- | :--- |
| `list(session_id)` | `session_id: str` | List contacts for a session |
| `get(session_id, contact_id)` | `session_id: str, contact_id: str` | Get contact profile |
| `block(session_id, contact_id)` | `session_id: str, contact_id: str` | Block a contact |
| `unblock(session_id, contact_id)` | `session_id: str, contact_id: str` | Unblock a contact |

---

## 5. Groups (`client.groups`)

| Method | Parameters | Description |
| :--- | :--- | :--- |
| `list(session_id)` | `session_id: str` | List group chats for a session |
| `get(session_id, group_id)` | `session_id: str, group_id: str` | Get group metadata |
| `create(session_id, data)` | `session_id: str, data: dict` | Create a new group chat |
| `add_participants(session_id, group_id, data)` | `session_id: str, group_id: str, data: dict` | Add phone numbers to group |
| `remove_participants(session_id, group_id, data)` | `session_id: str, group_id: str, data: dict` | Remove participants from group |
| `promote_participants(session_id, group_id, data)` | `session_id: str, group_id: str, data: dict` | Make participants admins |
| `demote_participants(session_id, group_id, data)` | `session_id: str, group_id: str, data: dict` | Remove admin privileges |
| `leave(session_id, group_id)` | `session_id: str, group_id: str` | Leave group chat |

---

## 6. API Keys (`client.api_keys`)

| Method | Parameters | Description |
| :--- | :--- | :--- |
| `list()` | - | List active API keys |
| `create(data)` | `data: dict` | Generate a new API key with roles and scopes |
| `delete(key_id)` | `key_id: str` | Revoke an API key |
