from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.strings import get_text
from bot.strings.keys import FEEDBACK_NEGATIVE, FEEDBACK_POSITIVE


def feedback_keyboard(
    processed_message_pk: int,
    lang: str | None = "en",
) -> InlineKeyboardMarkup:
    # Buttons are rendered for bot-chat feedback only in the current MVP.
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(FEEDBACK_POSITIVE, lang=lang or "en"),
                    callback_data=f"feedback:{processed_message_pk}:up",
                ),
                InlineKeyboardButton(
                    text=get_text(FEEDBACK_NEGATIVE, lang=lang or "en"),
                    callback_data=f"feedback:{processed_message_pk}:down",
                ),
            ]
        ]
    )
