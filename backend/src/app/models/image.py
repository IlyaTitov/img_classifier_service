from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime, func
from datetime import datetime
from .base import Base
from typing import List


class Image(Base):
    __tablename__ = "image"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    detections: Mapped[List["Detection"]] = relationship(
        back_populates="image",
        cascade="all, delete-orphan",
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="image")

    original_path: Mapped[str] = mapped_column(nullable=False)
    processed_path: Mapped[str] = mapped_column(nullable=True)
    file_size: Mapped[int] = mapped_column(nullable=True, default=0)
