import pytest

from bot.services.user import get_or_create_user


@pytest.mark.asyncio
async def test_get_or_create_user_creates_once(db_session) -> None:
    user = await get_or_create_user(
        session=db_session,
        telegram_id=123456,
        username="example_user",
        first_name="Example",
        last_name=None,
        language_code="en",
    )

    same_user = await get_or_create_user(
        session=db_session,
        telegram_id=123456,
        username="example_user",
        first_name="Example",
        last_name=None,
        language_code="en",
    )

    assert user.id == same_user.id
    assert same_user.username == "example_user"
