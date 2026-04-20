from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class EventType(Base):
    pass


class Event(Base):
    __tablename__ = "event"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[EventType] = mapped_column(nullable=True)
