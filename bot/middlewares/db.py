from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.utils.logger import logger


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Update):
            msg = event.message or event.channel_post or event.callback_query
            user = getattr(msg, "from_user", None)
            if user:
                logger.info(f"DEBUG user_id={user.id} username=@{user.username} cmd={getattr(msg, 'text', '')!r}")
        async with self._session_factory() as session:
            data["session"] = session
            return await handler(event, data)

