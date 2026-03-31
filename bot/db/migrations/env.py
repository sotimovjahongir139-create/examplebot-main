from logging.config import fileConfig

from alembic import context

from bot.config import get_settings
from bot.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    settings = get_settings()
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    raise RuntimeError(
        "Alembic online migrations should be run via the configured SQLAlchemy URL."
    )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

