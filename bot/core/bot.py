import asyncio

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import bot.state as bot_state
from bot.config import Settings, get_settings
from bot.db.connection import close_engine, create_session_factory, init_engine
from bot.db.migrations import run_startup_migrations
from bot.handlers import register_routers
from bot.middlewares.db import DbSessionMiddleware
from bot.services.dashboard import build_dashboard_text
from bot.utils.logger import configure_logging, logger
from database import init_db


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
    await init_db()
    logger.info("Bot startup completed")


async def on_shutdown() -> None:
    await close_engine()
    logger.info("Bot shutdown completed")


async def run_polling(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    await on_startup(settings)
    bot = create_bot(settings)

    me = await bot.get_me()
    bot_state.bot_username = me.username or ""
    logger.info(f"Bot username: @{bot_state.bot_username}")

    dispatcher = create_dispatcher(settings)

    scheduler: AsyncIOScheduler | None = None
    if settings.admin_id:
        admin_id = settings.admin_id

        async def _send_weekly_report() -> None:
            try:
                text = await build_dashboard_text()
                await bot.send_message(admin_id, text)
            except Exception as exc:
                logger.error(f"Weekly report failed: {exc}")

        scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Tashkent"))
        scheduler.add_job(_send_weekly_report, CronTrigger(day_of_week="fri", hour=9, minute=0))
        scheduler.start()
        logger.info("Weekly report scheduler started")

    try:
        await dispatcher.start_polling(bot)
    finally:
        if scheduler is not None:
            scheduler.shutdown()
        await bot.session.close()
        await on_shutdown()


def main() -> None:
    asyncio.run(run_polling())
