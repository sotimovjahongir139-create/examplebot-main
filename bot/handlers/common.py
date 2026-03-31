from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import get_settings
from bot.services.message_processing import process_owner_message, store_feedback
from bot.services.user import get_or_create_user
from bot.strings import get_text
from bot.strings.keys import (
    FEEDBACK_ERROR,
    FEEDBACK_PROMPT,
    FEEDBACK_SAVED,
    HELP,
    PROCESSING_DONE,
    UNKNOWN_COMMAND,
    WELCOME,
)
from bot.ui.inline import feedback_keyboard
from bot.ui.reply import main_menu_keyboard

router = Router(name="common")


@router.message(Command("start"))
async def start_handler(message: Message, session: AsyncSession) -> None:
    user = await get_or_create_user(
        session=session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code,
    )
    text = get_text(
        WELCOME,
        lang=user.language_code or get_settings().default_language,
        name=user.first_name or "there",
    )
    await message.answer(text, reply_markup=main_menu_keyboard(user.language_code))


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    settings = get_settings()
    user_lang = (message.from_user.language_code if message.from_user else None) or settings.default_language
    text = get_text(HELP, lang=user_lang)
    await message.answer(text, reply_markup=main_menu_keyboard(user_lang))


@router.message(F.text.startswith("/"))
async def unknown_command_handler(message: Message) -> None:
    settings = get_settings()
    user_lang = (message.from_user.language_code if message.from_user else None) or settings.default_language
    text = get_text(UNKNOWN_COMMAND, lang=user_lang)
    await message.answer(text)


@router.message(F.text)
async def process_text_handler(message: Message, session: AsyncSession) -> None:
    if message.from_user is None:
        return

    settings = get_settings()
    user_lang = message.from_user.language_code or settings.default_language
    result = await process_owner_message(
        session=session,
        owner_telegram_id=message.from_user.id,
        contact_id=message.chat.id,
        original_text=message.text,
        language_code=user_lang,
    )
    caption = get_text(
        PROCESSING_DONE,
        lang=user_lang,
        message_id=result.message_id,
        date=result.send_date_mmddyyyy,
    )
    image_file = BufferedInputFile(result.table_image_bytes, filename=f"message_{result.message_id}.png")
    # Client-ready image is sent as a normal message so it can be forwarded cleanly.
    await message.answer_photo(
        photo=image_file,
        caption=caption,
    )
    # Feedback controls stay in bot chat as a separate message tied to processed result ID.
    await message.answer(
        get_text(FEEDBACK_PROMPT, lang=user_lang),
        reply_markup=feedback_keyboard(result.db_record_id, lang=user_lang),
    )


@router.callback_query(F.data.startswith("feedback:"))
async def feedback_callback_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    # MVP scope: callback feedback is tied to bot-chat UI, not external forwarded messages.
    settings = get_settings()
    user_lang = (callback.from_user.language_code if callback.from_user else None) or settings.default_language
    raw = callback.data or ""
    parts = raw.split(":")
    if len(parts) != 3:
        await callback.answer(get_text(FEEDBACK_ERROR, lang=user_lang), show_alert=True)
        return

    _, message_pk_raw, feedback_value = parts
    if feedback_value not in {"up", "down"}:
        await callback.answer(get_text(FEEDBACK_ERROR, lang=user_lang), show_alert=True)
        return

    try:
        message_pk = int(message_pk_raw)
    except ValueError:
        await callback.answer(get_text(FEEDBACK_ERROR, lang=user_lang), show_alert=True)
        return

    if callback.from_user is None:
        await callback.answer(get_text(FEEDBACK_ERROR, lang=user_lang), show_alert=True)
        return

    is_stored = await store_feedback(
        session=session,
        processed_message_pk=message_pk,
        user_telegram_id=callback.from_user.id,
        feedback_value=feedback_value,
    )
    if not is_stored:
        await callback.answer(get_text(FEEDBACK_ERROR, lang=user_lang), show_alert=True)
        return

    await callback.answer(get_text(FEEDBACK_SAVED, lang=user_lang), show_alert=False)
