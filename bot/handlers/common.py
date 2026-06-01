import asyncio
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

import bot.state as bot_state
from bot.config import get_settings
from bot.services.dashboard import (
    build_admin_monthly_dashboard,
    build_dashboard_text,
    build_user_dashboard_text,
)
from bot.services.message_processing import (
    ensure_visible_fallback_table,
    export_to_excel,
    parse_business_table,
    process_owner_message,
)
from bot.services.user import get_or_create_user
from bot.strings import get_text
from bot.strings.keys import HELP, UNKNOWN_COMMAND, WELCOME
from bot.ui.inline import rating_keyboard
from bot.ui.reply import main_menu_keyboard
from bot.utils.logger import logger
from database import save_rating

router = Router(name="common")


@router.message(Command("start"))
async def start_handler(message: Message, session: AsyncSession, command: CommandObject) -> None:
    # Deep-link: /start rate_{message_id}  — anyone can open and rate
    if command.args and command.args.startswith("rate_"):
        await message.answer("Xizmatni baholang 👇", reply_markup=rating_keyboard())
        return

    settings = get_settings()
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
        lang=user.language_code or settings.default_language,
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
    if message.from_user is None:
        return
    settings = get_settings()
    if settings.admin_id is not None and message.from_user.id == settings.admin_id:
        text = await build_dashboard_text()
    else:
        text = await build_user_dashboard_text(message.from_user.id)
    await message.answer(text)


@router.message(Command("admin_dashboard"))
async def admin_dashboard_handler(message: Message) -> None:
    if message.from_user is None:
        return
    settings = get_settings()
    if settings.admin_id is None or message.from_user.id != settings.admin_id:
        await message.answer("Bu buyruq faqat admin uchun.")
        return
    now = datetime.now()
    text = await build_admin_monthly_dashboard(now.year, now.month)
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

    try:
        parsed = parse_business_table(result.corrected_text or result.original_text)
        parsed = ensure_visible_fallback_table(parsed, result.corrected_text or result.original_text)
        export_to_excel(parsed, result.message_id, result.send_date_mmddyyyy)
    except Exception as exc:
        logger.warning(f"Excel export failed: {exc}")

    await asyncio.sleep(1)

    link = f"https://t.me/{bot_state.bot_username}?start=rate_{result.message_id}"
    rating_text = (
        f'🔗 <a href="{link}">Xizmatni baholang</a>\n\n'
        f"Xizmatni baholang 👇"
    )
    await message.answer(rating_text, reply_markup=rating_keyboard())


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

    try:
        rating = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer()
        return

    if rating < 1 or rating > 5:
        await callback.answer()
        return

    try:
        await save_rating(
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            rating=rating,
        )
    except Exception as exc:
        logger.error(f"save_rating failed: {exc}")
        await callback.answer("Xatolik yuz berdi ❌", show_alert=True)
        return

    if callback.message is not None:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        try:
            await callback.message.answer("Rahmat! Bahoingiz qabul qilindi ✅")
        except Exception:
            pass

    await callback.answer()
