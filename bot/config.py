from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    database_url: str = Field("sqlite+aiosqlite:///./bot.db", alias="DATABASE_URL")
    default_language: str = Field("en", alias="DEFAULT_LANGUAGE")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_path: str = Field("logs/bot.log", alias="LOG_PATH")
    bot_parse_mode: str = Field("HTML", alias="BOT_PARSE_MODE")
    admin_id: int | None = Field(None, alias="ADMIN_ID")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

