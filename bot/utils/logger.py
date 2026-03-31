from pathlib import Path
import sys

from loguru import logger

from bot.config import Settings


def configure_logging(settings: Settings) -> None:
    log_path = Path(settings.log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(sys.stdout, level=settings.log_level)
    logger.add(log_path, level=settings.log_level, rotation="10 MB", retention=5)


__all__ = ["configure_logging", "logger"]

