from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from bot.db.models.message import ContactCounter, MessageFeedback, ProcessedMessage  # noqa: E402,F401
from bot.db.models.user import User  # noqa: E402,F401
