from datetime import date

import pytest

from bot.db.repos import (
    create_feedback,
    create_processed_message,
    get_processed_message_by_pk,
)


@pytest.mark.asyncio
async def test_processed_message_and_feedback_round_trip(db_session) -> None:
    record = await create_processed_message(
        session=db_session,
        contact_id=1001,
        owner_telegram_id=1,
        message_id=1,
        language_code="en",
        original_text="hello",
        corrected_text="Hello",
        send_date=date(2026, 3, 30),
    )
    await create_feedback(
        session=db_session,
        processed_message_id=record.id,
        user_telegram_id=1,
        feedback_value="up",
    )
    await db_session.commit()

    loaded = await get_processed_message_by_pk(db_session, processed_message_pk=record.id)

    assert loaded is not None
    assert loaded.message_id == 1
    assert loaded.corrected_text == "Hello"
