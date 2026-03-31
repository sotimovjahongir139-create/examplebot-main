from sqlalchemy.ext.asyncio import AsyncEngine

from bot.db.connection import get_engine
from bot.db.models import Base


async def run_startup_migrations(engine: AsyncEngine | None = None) -> None:
    engine = engine or get_engine()
    if engine.dialect.name != "sqlite":
        return

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

