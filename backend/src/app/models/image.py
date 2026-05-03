from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import Base


class Image(Base):
    __tablename__ = "image"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    user: Mapped["User"] = relationship(back_populates="image")

    detections: Mapped[List["Detection"]] = relationship(
        back_populates="image",
        cascade="all, delete-orphan",
    )

    original_path: Mapped[str] = mapped_column(nullable=False)
    processed_path: Mapped[Optional[str]] = mapped_column(nullable=True)

    file_size: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)

    task_id: Mapped[Optional[str]] = mapped_column(nullable=True)

    processing_duration_ms: Mapped[Optional[int]] = mapped_column(nullable=True)

    detection_count: Mapped[int] = mapped_column(
        nullable=False, default=0, server_default="0"
    )
