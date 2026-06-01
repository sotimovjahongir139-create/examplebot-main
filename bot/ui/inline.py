from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def rating_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐1", callback_data="rate_1"),
                InlineKeyboardButton(text="⭐2", callback_data="rate_2"),
                InlineKeyboardButton(text="⭐3", callback_data="rate_3"),
                InlineKeyboardButton(text="⭐4", callback_data="rate_4"),
                InlineKeyboardButton(text="⭐5", callback_data="rate_5"),
            ]
        ]
    )
