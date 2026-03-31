from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.strings import get_text
from bot.strings.keys import HELP_BUTTON, START_BUTTON


def main_menu_keyboard(lang: str | None = "en") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(START_BUTTON, lang=lang or "en"))],
            [KeyboardButton(text=get_text(HELP_BUTTON, lang=lang or "en"))],
        ],
        resize_keyboard=True,
    )
