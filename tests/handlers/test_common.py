from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from bot.handlers.common import help_handler, process_text_handler, start_handler


@pytest.mark.asyncio
async def test_start_handler_answers_with_welcome(db_session) -> None:
    message = AsyncMock()
    message.from_user = SimpleNamespace(
        id=1,
        username="example_user",
        first_name="Example",
        last_name=None,
        language_code="en",
    )

    await start_handler(message, db_session)

    message.answer.assert_awaited_once()
    text = message.answer.await_args.args[0]
    assert "Welcome, Example!" in text


@pytest.mark.asyncio
async def test_help_handler_answers_with_help_text() -> None:
    message = AsyncMock()
    message.from_user = SimpleNamespace(language_code="en")

    await help_handler(message)

    message.answer.assert_awaited_once()
    text = message.answer.await_args.args[0]
    assert "Send your message exactly" in text


@pytest.mark.asyncio
async def test_process_text_handler_answers_with_photo(db_session) -> None:
    message = AsyncMock()
    message.text = "hello,world"
    message.chat = SimpleNamespace(id=1001)
    message.from_user = SimpleNamespace(
        id=10,
        language_code="en",
    )

    await process_text_handler(message, db_session)

    message.answer_photo.assert_awaited_once()
    caption = message.answer_photo.await_args.kwargs["caption"]
    assert "Qayta ishlangan xabar ID 1" in caption
    message.answer.assert_awaited()
    feedback_prompt = message.answer.await_args.args[0]
    assert "Ushbu xabarni baholang:" in feedback_prompt
