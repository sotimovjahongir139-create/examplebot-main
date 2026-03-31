from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repos
from bot.db.models.user import User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
    language_code: str | None,
) -> User:
    user = await repos.get_user(session, telegram_id)
    if user is not None:
        return user

    return await repos.create_user(
        session=session,
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code,
    )

