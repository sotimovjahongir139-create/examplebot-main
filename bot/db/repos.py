from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models.message import ContactCounter, MessageFeedback, ProcessedMessage
from bot.db.models.user import User


async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
    language_code: str | None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code or "en",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_contact_counter(session: AsyncSession, contact_id: int) -> ContactCounter | None:
    result = await session.execute(select(ContactCounter).where(ContactCounter.contact_id == contact_id))
    return result.scalar_one_or_none()


async def create_contact_counter(session: AsyncSession, contact_id: int) -> ContactCounter:
    counter = ContactCounter(contact_id=contact_id, next_message_id=1)
    session.add(counter)
    await session.flush()
    return counter


async def create_processed_message(
    session: AsyncSession,
    contact_id: int,
    owner_telegram_id: int,
    message_id: int,
    language_code: str,
    original_text: str,
    corrected_text: str,
    send_date: date,
) -> ProcessedMessage:
    record = ProcessedMessage(
        contact_id=contact_id,
        owner_telegram_id=owner_telegram_id,
        message_id=message_id,
        language_code=language_code,
        original_text=original_text,
        corrected_text=corrected_text,
        send_date=send_date,
    )
    session.add(record)
    await session.flush()
    return record


async def get_processed_message_by_pk(
    session: AsyncSession,
    processed_message_pk: int,
) -> ProcessedMessage | None:
    result = await session.execute(
        select(ProcessedMessage).where(ProcessedMessage.id == processed_message_pk)
    )
    return result.scalar_one_or_none()


async def create_feedback(
    session: AsyncSession,
    processed_message_id: int,
    user_telegram_id: int,
    feedback_value: str,
) -> MessageFeedback:
    feedback = MessageFeedback(
        processed_message_id=processed_message_id,
        user_telegram_id=user_telegram_id,
        feedback_value=feedback_value,
    )
    session.add(feedback)
    await session.flush()
    return feedback
