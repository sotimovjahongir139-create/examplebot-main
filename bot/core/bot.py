import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.config import Settings, get_settings
from bot.db.connection import close_engine, create_session_factory, init_engine
from bot.db.migrations import run_startup_migrations
from bot.handlers import register_routers
from bot.middlewares.db import DbSessionMiddleware
from bot.utils.logger import configure_logging, logger


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=settings.bot_parse_mode),
    )


def create_dispatcher(settings: Settings) -> Dispatcher:
    session_factory = create_session_factory()
    dispatcher = Dispatcher()
    dispatcher.update.middleware(DbSessionMiddleware(session_factory))
    register_routers(dispatcher)
    return dispatcher


async def on_startup(settings: Settings) -> None:
    configure_logging(settings)
    await init_engine(settings.database_url)
    await run_startup_migrations()
    logger.info("Bot startup completed")


async def on_shutdown() -> None:
    await close_engine()
    logger.info("Bot shutdown completed")


async def run_polling(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    await on_startup(settings)
    bot = create_bot(settings)
    dispatcher = create_dispatcher(settings)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await on_shutdown()


def main() -> None:
    asyncio.run(run_polling())

