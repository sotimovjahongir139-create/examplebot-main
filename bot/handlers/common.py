import asyncio
import uuid

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

import bot.state as bot_state
from bot.config import get_settings
from bot.services.dashboard import build_dashboard_text
from bot.services.message_processing import process_owner_message
from bot.services.user import get_or_create_user
from bot.strings import get_text
from bot.strings.keys import (
    HELP,
    PROCESSING_DONE,
    UNKNOWN_COMMAND,
    WELCOME,
)
from bot.ui.inline import rating_keyboard
from bot.ui.reply import main_menu_keyboard
from database import create_pending_rating, get_pending_rating, mark_rating_used, save_rating

router = Router(name="common")


@router.message(Command("start"))
async def start_handler(message: Message, session: AsyncSession, command: CommandObject) -> None:
    # Deep-link flow: /start rate_<token>
    if command.args and command.args.startswith("rate_"):
        token = command.args[len("rate_"):]
        pending = await get_pending_rating(token)
        if pending is None or pending["used"]:
            await message.answer("Bu havola allaqachon ishlatilgan ❌")
            return
        await message.answer("Xizmatimizni baholang 👇", reply_markup=rating_keyboard(token))
        return

    # Normal /start
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


@router.message(Command("dashboard"))
async def dashboard_handler(message: Message) -> None:
    settings = get_settings()
    if settings.admin_id is None or message.from_user is None or message.from_user.id != settings.admin_id:
        await message.answer("Bu buyruq faqat admin uchun.")
        return
    text = await build_dashboard_text()
    await message.answer(text)


@router.message(F.text.startswith("/"))
async def unknown_command_handler(message: Message) -> None:
    settings = get_settings()
    user_lang = (message.from_user.language_code if message.from_user else None) or settings.default_language
    text = get_text(UNKNOWN_COMMAND, lang=user_lang)
    await message.answer(text)


async def _process_and_rate(message: Message, session: AsyncSession) -> None:
    settings = get_settings()
    owner_id = message.from_user.id if message.from_user else message.chat.id
    user_lang = (message.from_user.language_code if message.from_user else None) or settings.default_language
    text_content = message.text or message.caption or ""

    result = await process_owner_message(
        session=session,
        owner_telegram_id=owner_id,
        contact_id=message.chat.id,
        original_text=text_content,
        language_code=user_lang,
    )
    caption = get_text(
        PROCESSING_DONE,
        lang=user_lang,
        message_id=result.message_id,
        date=result.send_date_mmddyyyy,
    )
    image_file = BufferedInputFile(result.table_image_bytes, filename=f"message_{result.message_id}.png")
    await message.answer_photo(photo=image_file, caption=caption)

    token = uuid.uuid4().hex
    await create_pending_rating(token)

    await asyncio.sleep(1)
    link = f"t.me/{bot_state.bot_username}?start=rate_{token}"
    await message.answer(f"Xizmatni baholang: {link}")


@router.message(F.text)
async def process_text_handler(message: Message, session: AsyncSession) -> None:
    await _process_and_rate(message, session)


@router.channel_post(F.text)
async def process_channel_post_handler(message: Message, session: AsyncSession) -> None:
    await _process_and_rate(message, session)


@router.callback_query(F.data.startswith("rate_"))
async def rating_callback_handler(callback: CallbackQuery) -> None:
    if callback.from_user is None or callback.data is None:
        await callback.answer()
        return

    # callback_data format: "rate_<N>:<token>"
    parts = callback.data.split(":", 1)
    if len(parts) != 2:
        await callback.answer()
        return

    try:
        rating = int(parts[0].split("_")[1])
    except (IndexError, ValueError):
        await callback.answer()
        return

    token = parts[1]
    pending = await get_pending_rating(token)
    if pending is None or pending["used"]:
        await callback.answer("Bu havola allaqachon ishlatilgan ❌", show_alert=True)
        return

    await mark_rating_used(token)
    await save_rating(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        rating=rating,
    )

    if callback.message is not None:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    await callback.answer("Rahmat! Bahoingiz qabul qilindi ✅", show_alert=True)
