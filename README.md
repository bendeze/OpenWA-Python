<div align="center">
  <img src="https://raw.githubusercontent.com/bendeze/OpenWA-Python/main/docs/logo/openwa_logo.png" alt="OpenWA Logo" width="200"/>
  <h1>OpenWA-Python</h1>
  <p>Python SDK & Bot Framework for the <a href="https://github.com/rmyndharis/OpenWA">OpenWA</a> WhatsApp API Gateway.</p>

  <p>
    <a href="https://github.com/bendeze/openwa-python/stargazers"><img src="https://img.shields.io/github/stars/bendeze/openwa-python?style=flat-square" alt="Stars" /></a>
    <a href="https://github.com/bendeze/openwa-python/network/members"><img src="https://img.shields.io/github/forks/bendeze/openwa-python?style=flat-square" alt="Forks" /></a>
    <a href="https://github.com/bendeze/openwa-python/issues"><img src="https://img.shields.io/github/issues/bendeze/openwa-python?style=flat-square" alt="Issues" /></a>
    <a href="https://github.com/bendeze/openwa-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/bendeze/openwa-python?style=flat-square" alt="License" /></a>
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square" alt="Python Version" />
  </p>
</div>

---

## 📖 Overview

**OpenWA-Python** (`openwa-sdk`) is the Python client library and bot framework for [OpenWA](https://github.com/rmyndharis/OpenWA) (the open-source, self-hosted WhatsApp API Gateway).

### Key Features

* 🤖 **High-Level Bot Framework**: Decorator-driven command and message routing (`@bot.on_command`, `@bot.on_message`, `@bot.on_media`).
* 🔄 **Finite State Machine (FSM)**: Multi-step conversation state management (`StatesGroup`, `State`, `MemoryStorage`).
* ⚡ **Sync & Async REST Clients**: Type-safe HTTP clients with `httpx` and `pydantic`.
* 💬 **Rich Context Actions**: `await ctx.reply()`, `await ctx.react("👍")`, `await ctx.quote()`, `await ctx.reply_image()`.
* 🪝 **Webhook Dispatcher**: One-line integration into FastAPI, Flask, or Django (`await bot.feed_raw_event(payload)`).

---

## 🚀 Quickstart

### 1. Start the OpenWA Engine

Run the official OpenWA engine container for local development:

```bash
docker compose up -d
```
The OpenWA REST API and dashboard will be available at `http://localhost:3000`.

### 2. Install the Python SDK

```bash
pip install openwa-sdk
# or install from source in editable mode:
pip install -e .
```

### 3. Build a WhatsApp Bot (`OpenWABot`)

```python
from openwa import OpenWABot, Context, StatesGroup, State

bot = OpenWABot(base_url="http://localhost:3000", api_key="your_api_key")

# Command handler
@bot.on_command("start")
async def handle_start(ctx: Context):
    await ctx.reply("👋 Welcome to our WhatsApp Bot!")

# Echo command with arguments
@bot.on_command("echo")
async def handle_echo(ctx: Context):
    await ctx.reply(f"🔊 Echo: {ctx.command_args}")

# Multi-step conversation using FSM
class FeedbackForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_feedback = State()

@bot.on_command("feedback")
async def start_feedback(ctx: Context):
    await ctx.set_state(FeedbackForm.waiting_for_name)
    await ctx.reply("What is your name?")

@bot.on_message(state=FeedbackForm.waiting_for_name)
async def process_name(ctx: Context):
    await ctx.update_data(name=ctx.text)
    await ctx.set_state(FeedbackForm.waiting_for_feedback)
    await ctx.reply(f"Nice to meet you {ctx.text}! What feedback do you have?")

@bot.on_message(state=FeedbackForm.waiting_for_feedback)
async def process_feedback(ctx: Context):
    data = await ctx.get_data()
    await ctx.clear_state()
    await ctx.reply(f"✅ Thank you {data['name']}, feedback saved!")
```

### 4. Direct REST Client Usage

```python
from openwa import OpenWAClient

client = OpenWAClient(base_url="http://localhost:3000", api_key="your_api_key")

# Send a direct message
client.messages.send_text(
    session_id="default",
    data={"chatId": "1234567890@c.us", "text": "Hello from OpenWA!"}
)
```

---

## 📚 Documentation

Detailed documentation is available in the [`docs/`](file:///home/bonheur/openwa_python/docs) directory:

- [01 - Getting Started](./docs/01-getting-started.md)
- [02 - Architecture](./docs/02-architecture.md)
- [03 - SDK & Bot Framework Reference](./docs/03-sdk-reference.md)
- [04 - Development & Testing](./docs/04-development-testing.md)

---

## 🧪 Testing

```bash
# Run unit test suite
pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](file:///home/bonheur/openwa_python/LICENSE) file for details.
