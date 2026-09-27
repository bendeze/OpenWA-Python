# 02 - Architecture

## 1. System Overview

OpenWA-Python provides a dual-layer architecture:
1. **The Engine Layer (Docker)**: Runs the upstream OpenWA engine (handling Chromium browser instances, Baileys WebSocket sessions, and WhatsApp Web protocol reverse engineering).
2. **The Python Framework Layer (This Package)**: Provides typed REST clients, decorator-driven event routing, context reply actions, and conversation state management.

```text
┌────────────────────────────────────────────────────────┐
│             UPSTREAM OPENWA ENGINE (Docker)            │
│  - Container: ghcr.io/rmyndharis/openwa                │
│  - Manages WhatsApp Web protocols & Chromium instances │
│  - Exposes REST API & Webhooks on port 3000            │
└───────────────────────────▲────────────────────────────┘
                            │
               HTTP REST / Webhook Events
                            │
┌───────────────────────────▼────────────────────────────┐
│                OPENWA-PYTHON (This SDK)                │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │               OpenWABot (Event Router)           │  │
│  │   • @bot.on_command()     • @bot.on_message()    │  │
│  │   • @bot.on_media()       • @bot.on_reaction()   │  │
│  │   • FSM Conversation State Management            │  │
│  └──────────────────────────┬───────────────────────┘  │
│                             │                          │
│                             ▼                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │             Context Action Helpers (ctx)         │  │
│  │   • ctx.reply()           • ctx.react()          │  │
│  │   • ctx.reply_image()     • ctx.quote()          │  │
│  └──────────────────────────┬───────────────────────┘  │
│                             │                          │
│                             ▼                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │           AsyncOpenWAClient / OpenWAClient       │  │
│  │   • sessions  • messages  • webhooks             │  │
│  │   • contacts  • groups    • api_keys             │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 2. Event Dispatching Lifecycle

When an incoming WhatsApp message arrives:

```text
[WhatsApp User] ──> (Sends message)
       │
       ▼
[OpenWA Engine] ──> (Dispatches HTTP POST to webhook endpoint)
       │
       ▼
[FastAPI / Django] ──> (Calls `await bot.feed_raw_event(payload)`)
       │
       ▼
[OpenWABot] ──> (Normalizes payload into `EventPayload` & `MessagePayload`)
       │
       ▼
[Context] ──> (Wraps message, client, and FSM memory storage)
       │
       ▼
[Router] ──> (Evaluates command names, regex patterns, media types & FSM states)
       │
       ▼
[Your Handler Function] ──> (`async def handle_cmd(ctx): await ctx.reply(...)`)
```

---

## 3. Finite State Machine (FSM) Architecture

The FSM enables multi-step user dialogues without external database boilerplate:

- **State Identity**: Each `State` has a qualified name `GroupName:state_name`.
- **Storage Key**: States and conversation data are keyed by `(session_id, chat_id, sender_id)` to isolate user sessions.
- **MemoryStorage**: High-speed, non-blocking in-memory state store (pluggable for future Redis/database backends via `BaseStorage`).
