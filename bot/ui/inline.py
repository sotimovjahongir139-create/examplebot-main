from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def rating_keyboard(token: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ 1", callback_data=f"rate_1:{token}"),
                InlineKeyboardButton(text="⭐ 2", callback_data=f"rate_2:{token}"),
                InlineKeyboardButton(text="⭐ 3", callback_data=f"rate_3:{token}"),
                InlineKeyboardButton(text="⭐ 4", callback_data=f"rate_4:{token}"),
                InlineKeyboardButton(text="⭐ 5", callback_data=f"rate_5:{token}"),
            ]
        ]
    )
