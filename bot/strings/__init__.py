from bot.config import get_settings
from bot.strings.strings import STRINGS


def get_text(key: str, lang: str | None = None, **kwargs: object) -> str:
    default_language = get_settings().default_language
    lang = lang or default_language
    translations = STRINGS.get(lang) or STRINGS[default_language]
    template = translations.get(key) or STRINGS[default_language].get(key, key)
    return template.format(**kwargs)

