# 03 - SDK & Bot Framework Reference

The `openwa` package provides both low-level REST clients (`OpenWAClient`, `AsyncOpenWAClient`) and a high-level decorator-driven bot framework (`OpenWABot`).

---

## 1. High-Level Bot Framework (`OpenWABot`)

The `OpenWABot` class provides an event-driven bot framework with command dispatching, regex pattern matching, media routing, and conversation state management (FSM).

```python
from openwa import OpenWABot, Context, StatesGroup, State, MediaType

bot = OpenWABot(base_url="http://localhost:3000", api_key="secret")
```

### Decorators

| Decorator | Parameters | Description |
| :--- | :--- | :--- |
| `@bot.on_command(command, prefixes, state, is_group)` | `command: str \| list[str]`, `prefixes: tuple = ('/', '!')`, `state: Optional[State]`, `is_group: Optional[bool]` | Handles WhatsApp commands (e.g. `/start`, `!help`). |
| `@bot.on_message(pattern, state, is_group)` | `pattern: Optional[str \| Pattern]`, `state: Optional[State]`, `is_group: Optional[bool]` | Handles incoming text messages matching optional regex or state. |
| `@bot.on_media(media_type, state, is_group)` | `media_type: Optional[MediaType \| list[MediaType]]`, `state: Optional[State]` | Handles incoming media (images, audio, video, voice notes, documents). |
| `@bot.on_reaction(state)` | `state: Optional[State]` | Handles message reaction emoji events. |
| `@bot.on_event(event_type, state)` | `event_type: EventType \| str`, `state: Optional[State]` | Handles system events (e.g. `qr`, `session_status`). |

### Context Object (`Context`)

Every handler receives a rich `ctx: Context` object:

| Property / Method | Returns | Description |
| :--- | :--- | :--- |
| `ctx.message` | `MessagePayload` | Normalized incoming message data |
| `ctx.chat_id` | `str` | Chat identifier (e.g. `1234567890@c.us` or `..._group@g.us`) |
| `ctx.sender_id` | `str` | Author phone / WhatsApp ID |
| `ctx.text` | `Optional[str]` | Message text or caption |
| `ctx.command` | `Optional[str]` | Command name (e.g. `/start`) |
| `ctx.command_args` | `str` | Arguments passed after the command |
| `await ctx.reply(text)` | `MessageResponse` | Send text reply to current chat |
| `await ctx.reply_image(file, caption)` | `dict` | Send image to current chat |
| `await ctx.reply_file(file, caption, filename)` | `dict` | Send document / file |
| `await ctx.reply_location(lat, lng, title)` | `dict` | Send GPS location |
| `await ctx.reply_poll(name, options)` | `dict` | Send interactive poll |
| `await ctx.react(emoji)` | `dict` | React to incoming message with emoji |
| `await ctx.quote(text)` | `dict` | Reply quoting incoming message |
| `await ctx.get_state()` | `Optional[str]` | Get user's current FSM conversation state |
| `await ctx.set_state(state)` | `None` | Set user's FSM state |
| `await ctx.clear_state()` | `None` | Reset FSM state |
| `await ctx.get_data()` | `dict` | Retrieve stored context data |
| `await ctx.update_data(**kwargs)` | `dict` | Update stored context data |
| `await ctx.clear_data()` | `None` | Clear stored context data |

### Finite State Machine (FSM)

```python
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()

@bot.on_command("register")
async def start_register(ctx: Context):
    await ctx.set_state(Registration.waiting_for_name)
    await ctx.reply("What is your name?")

@bot.on_message(state=Registration.waiting_for_name)
async def process_name(ctx: Context):
    await ctx.update_data(name=ctx.text)
    await ctx.set_state(Registration.waiting_for_email)
    await ctx.reply(f"Thanks {ctx.text}! What is your email?")
```

### Feeding Webhook Events

When receiving webhooks in FastAPI, Flask, or Django:

```python
@app.post("/webhook")
async def webhook_handler(payload: dict):
    handled = await bot.feed_raw_event(payload)
    return {"handled": handled}
```

---

## 2. Low-Level Client API (`OpenWAClient` & `AsyncOpenWAClient`)

### Sessions (`client.sessions`)

| Method | Description |
| :--- | :--- |
| `list()` | List all configured sessions |
| `get(session_id)` | Get session metadata |
| `create(name)` | Create new session |
| `start(session_id)` | Start session WhatsApp connection |
| `stop(session_id)` | Disconnect session |
| `restart(session_id)` | Restart session |
| `delete(session_id)` | Delete session and token data |
| `qr(session_id)` | Retrieve QR code for login |
| `status(session_id)` | Check session status |

### Messages (`client.messages`)

| Method | Description |
| :--- | :--- |
| `send_text(session_id, data)` | Send text message (`{"chatId": "...", "text": "..."}`) |
| `send_image(session_id, data)` | Send image (`{"chatId": "...", "file": "...", "caption": "..."}`) |
| `send_file(session_id, data)` | Send document/file |
| `send_location(session_id, data)` | Send location |
| `send_poll(session_id, data)` | Create WhatsApp poll |
| `send_reaction(session_id, data)` | React to message |
| `reply(session_id, data)` | Quote and reply to message |
| `delete(session_id, message_id)` | Revoke sent message |

### Webhooks, Contacts, Groups, & API Keys

- `client.webhooks`: `list()`, `create(data)`, `update(id, data)`, `delete(id)`
- `client.contacts`: `list(session_id)`, `get(session_id, contact_id)`, `block(...)`, `unblock(...)`
- `client.groups`: `list(session_id)`, `create(session_id, data)`, `add_participants(...)`, `remove_participants(...)`, `leave(...)`
- `client.api_keys`: `list()`, `create(data)`, `delete(id)`
