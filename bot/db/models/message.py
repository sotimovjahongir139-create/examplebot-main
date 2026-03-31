from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.db.models import Base


class ContactCounter(Base):
    __tablename__ = "contact_counters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    next_message_id: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"
    __table_args__ = (UniqueConstraint("contact_id", "message_id", name="uq_contact_message"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contact_id: Mapped[int] = mapped_column(BigInteger, index=True)
    owner_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[int] = mapped_column(Integer, index=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en")
    original_text: Mapped[str] = mapped_column(Text)
    corrected_text: Mapped[str] = mapped_column(Text)
    send_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    feedback: Mapped[list["MessageFeedback"]] = relationship(
        back_populates="processed_message",
        cascade="all, delete-orphan",
    )


class MessageFeedback(Base):
    __tablename__ = "message_feedback"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    processed_message_id: Mapped[int] = mapped_column(ForeignKey("processed_messages.id"), index=True)
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    feedback_value: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_message: Mapped[ProcessedMessage] = relationship(back_populates="feedback")
