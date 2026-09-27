"""
Example: Building a WhatsApp Bot with OpenWA Bot Framework & FSM.
"""

import asyncio

from openwa import Context, MediaType, OpenWABot, State, StatesGroup


# 1. Define FSM Conversation States
class SurveyForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_feedback = State()


# 2. Initialize Bot
bot = OpenWABot(base_url="http://localhost:3000", api_key="your_api_key_here")


# 3. Register Command Handlers
@bot.on_command("start")
async def handle_start(ctx: Context):
    await ctx.reply(
        "👋 Welcome to OpenWA Bot!\n\n"
        "Commands:\n"
        "• /start - Show this welcome message\n"
        "• /survey - Start a feedback questionnaire\n"
        "• /echo <text> - Repeat your text\n"
        "• /help - Get assistance"
    )


@bot.on_command("echo")
async def handle_echo(ctx: Context):
    text = ctx.command_args or "You didn't provide any text to echo!"
    await ctx.reply(f"🔊 Echo: {text}")


# 4. Multi-Step Form with FSM
@bot.on_command("survey")
async def start_survey(ctx: Context):
    await ctx.set_state(SurveyForm.waiting_for_name)
    await ctx.reply("📝 What is your full name?")


@bot.on_message(state=SurveyForm.waiting_for_name)
async def process_name(ctx: Context):
    await ctx.update_data(name=ctx.text)
    await ctx.set_state(SurveyForm.waiting_for_feedback)
    await ctx.reply(f"Nice to meet you, {ctx.text}! What feedback do you have for us?")


@bot.on_message(state=SurveyForm.waiting_for_feedback)
async def process_feedback(ctx: Context):
    data = await ctx.get_data()
    name = data.get("name", "User")
    feedback = ctx.text

    # Clear state when finished
    await ctx.clear_state()

    await ctx.reply(
        f'✅ Thank you {name}! Your feedback has been recorded:\n\n"{feedback}"'
    )


# 5. Media Handler
@bot.on_media(MediaType.IMAGE)
async def handle_image(ctx: Context):
    await ctx.reply("🖼️ Nice image! Thanks for sharing.")


# 6. Incoming Webhook Simulation
async def main():
    print("🤖 Simulating incoming webhook events...")

    # Simulate /start command
    await bot.feed_raw_event(
        {
            "event": "message",
            "session": "default",
            "data": {
                "id": "msg_001",
                "from": "1234567890@c.us",
                "body": "/start",
            },
        }
    )

    print("✅ Webhook simulation complete.")


if __name__ == "__main__":
    asyncio.run(main())
