# 01 - Getting Started

This guide walks you through setting up the OpenWA engine, sending direct WhatsApp messages, and building your first event-driven bot using the Python framework.

---

## 1. Prerequisites

- Python 3.9 or higher
- Docker & Docker Compose (for running the OpenWA engine locally)

---

## 2. Start the OpenWA Engine

Run the official OpenWA engine container using Docker Compose:

```bash
docker compose up -d
```

This starts the OpenWA server at `http://localhost:3000`. You can open `http://localhost:3000` in your browser to access the visual QR code and session dashboard.

---

## 3. Install the Python SDK

Install the package:

```bash
pip install openwa-sdk
# or in editable mode for development:
pip install -e .
```

---

## 4. Sending Direct Messages (Low-Level Client)

### Synchronous Client

```python
from openwa import OpenWAClient

# 1. Initialize client
client = OpenWAClient(base_url="http://localhost:3000", api_key="your_api_key")

# 2. List active WhatsApp sessions
sessions = client.sessions.list()
print("Sessions:", sessions)

# 3. Send a text message
client.messages.send_text(
    session_id="default",
    data={
        "chatId": "1234567890@c.us",
        "text": "Hello from OpenWA Python!"
    }
)
```

### Asynchronous Client

```python
import asyncio
from openwa import AsyncOpenWAClient

async def main():
    async with AsyncOpenWAClient(base_url="http://localhost:3000", api_key="your_api_key") as client:
        # Send an async message
        response = await client.messages.send_text(
            session_id="default",
            data={
                "chatId": "1234567890@c.us",
                "text": "Async message sent via OpenWA!"
            }
        )
        print("Message sent:", response)

asyncio.run(main())
```

---

## 5. Building Your First Bot (`OpenWABot`)

To build an interactive bot that responds to incoming WhatsApp messages:

```python
from openwa import OpenWABot, Context

# 1. Initialize the Bot
bot = OpenWABot(base_url="http://localhost:3000", api_key="your_api_key")

# 2. Handle /start command
@bot.on_command("start")
async def handle_start(ctx: Context):
    await ctx.reply("👋 Hello! Welcome to my WhatsApp bot.")

# 3. Handle /echo command with arguments
@bot.on_command("echo")
async def handle_echo(ctx: Context):
    await ctx.reply(f"🔊 Echo: {ctx.command_args}")

# 4. Handle text messages matching regex
@bot.on_message(pattern=r"^(hi|hello|hey)")
async def handle_greetings(ctx: Context):
    await ctx.reply("Hello there! How can I help you today?")
```

### Connecting to a FastAPI Webhook Server

When OpenWA forwards incoming events to your server:

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def receive_whatsapp_event(request: Request):
    payload = await request.json()
    # bot.feed_raw_event parses and routes the event to your handlers
    handled = await bot.feed_raw_event(payload)
    return {"handled": handled}
```
