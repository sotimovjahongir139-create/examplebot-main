import pytest

from bot.db.repos import create_user, get_user


@pytest.mark.asyncio
async def test_user_model_round_trip(db_session) -> None:
    created = await create_user(
        session=db_session,
        telegram_id=999,
        username="example",
        first_name="Example",
        last_name="User",
        language_code="en",
    )

    loaded = await get_user(db_session, telegram_id=999)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.first_name == "Example"

