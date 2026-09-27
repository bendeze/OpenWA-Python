"""
Unit tests for OpenWA Bot Framework & Router.
"""

import unittest
from unittest.mock import AsyncMock, patch

from openwa.bot import (
    Context,
    EventPayload,
    EventType,
    MediaType,
    MemoryStorage,
    MessagePayload,
    OpenWABot,
    Router,
    SenderInfo,
    State,
    StatesGroup,
)


class FormStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()


class TestBotFramework(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.bot = OpenWABot(base_url="http://localhost:3000", api_key="secret")
        self.bot.client._request = AsyncMock(return_value={"status": "success"})

    def _create_message_event(
        self,
        text: str = "hello",
        chat_id: str = "1234567890@c.us",
        session_id: str = "default",
        media_type: MediaType = MediaType.NONE,
    ) -> EventPayload:
        return EventPayload(
            event=EventType.MESSAGE,
            session_id=session_id,
            message=MessagePayload(
                id="msg_001",
                session_id=session_id,
                chat_id=chat_id,
                sender=SenderInfo(id=chat_id, name="Test User"),
                text=text,
                has_media=(media_type != MediaType.NONE),
                media_type=media_type,
            ),
        )

    async def test_command_handling(self):
        called = False

        @self.bot.on_command("start")
        async def handle_start(ctx: Context):
            nonlocal called
            called = True
            self.assertEqual(ctx.command, "/start")
            self.assertEqual(ctx.chat_id, "1234567890@c.us")
            await ctx.reply("Welcome!")

        # Trigger /start
        event = self._create_message_event(text="/start")
        result = await self.bot.feed_event(event)

        self.assertTrue(result)
        self.assertTrue(called)
        self.bot.client._request.assert_awaited_once_with(
            "POST",
            "/api/sessions/default/messages/text",
            {"chatId": "1234567890@c.us", "text": "Welcome!"},
        )

    async def test_command_args_extraction(self):
        args_received = ""

        @self.bot.on_command("echo")
        async def handle_echo(ctx: Context):
            nonlocal args_received
            args_received = ctx.command_args

        event = self._create_message_event(text="/echo hello world from test")
        await self.bot.feed_event(event)

        self.assertEqual(args_received, "hello world from test")

    async def test_regex_message_handling(self):
        matched = False

        @self.bot.on_message(pattern=r"^order:\s*(\d+)$")
        async def handle_order(ctx: Context):
            nonlocal matched
            matched = True

        # Non-matching text
        await self.bot.feed_event(self._create_message_event(text="hello order"))
        self.assertFalse(matched)

        # Matching text
        await self.bot.feed_event(self._create_message_event(text="order: 9982"))
        self.assertTrue(matched)

    async def test_media_handling(self):
        image_received = False

        @self.bot.on_media(MediaType.IMAGE)
        async def handle_image(ctx: Context):
            nonlocal image_received
            image_received = True

        # Send text message -> should not match
        await self.bot.feed_event(self._create_message_event(text="my photo"))
        self.assertFalse(image_received)

        # Send image message -> should match
        img_event = self._create_message_event(media_type=MediaType.IMAGE)
        await self.bot.feed_event(img_event)
        self.assertTrue(image_received)

    async def test_fsm_conversation_flow(self):
        @self.bot.on_command("register")
        async def start_register(ctx: Context):
            await ctx.set_state(FormStates.waiting_for_name)
            await ctx.reply("What is your name?")

        @self.bot.on_message(state=FormStates.waiting_for_name)
        async def process_name(ctx: Context):
            await ctx.update_data(name=ctx.text)
            await ctx.set_state(FormStates.waiting_for_age)
            await ctx.reply("What is your age?")

        @self.bot.on_message(state=FormStates.waiting_for_age)
        async def process_age(ctx: Context):
            data = await ctx.get_data()
            await ctx.clear_state()
            await ctx.reply(f"Registered {data['name']}, age {ctx.text}")

        # 1. Start registration
        await self.bot.feed_event(self._create_message_event(text="/register"))
        self.assertEqual(
            await self.bot.storage.get_state(("default", "1234567890@c.us", "1234567890@c.us")),
            "FormStates:waiting_for_name",
        )

        # 2. Provide name
        await self.bot.feed_event(self._create_message_event(text="Alice"))
        self.assertEqual(
            await self.bot.storage.get_state(("default", "1234567890@c.us", "1234567890@c.us")),
            "FormStates:waiting_for_age",
        )

        # 3. Provide age
        await self.bot.feed_event(self._create_message_event(text="28"))
        self.assertIsNone(
            await self.bot.storage.get_state(("default", "1234567890@c.us", "1234567890@c.us"))
        )

    async def test_sub_router(self):
        admin_router = Router(name="admin")
        admin_called = False

        @admin_router.on_command("admin")
        async def handle_admin(ctx: Context):
            nonlocal admin_called
            admin_called = True

        self.bot.include_router(admin_router)

        await self.bot.feed_event(self._create_message_event(text="/admin"))
        self.assertTrue(admin_called)

    async def test_raw_webhook_parsing(self):
        handled = False

        @self.bot.on_command("ping")
        async def handle_ping(ctx: Context):
            nonlocal handled
            handled = True

        raw_payload = {
            "event": "message",
            "session": "prod_session",
            "data": {
                "id": "true_1234@c.us_ABCDEF",
                "from": "1234@c.us",
                "body": "!ping",
                "timestamp": 1700000000,
            },
        }

        result = await self.bot.feed_raw_event(raw_payload)
        self.assertTrue(result)
        self.assertTrue(handled)


if __name__ == "__main__":
    unittest.main()
