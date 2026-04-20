from sqalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ObjectType(Base):
    __tablename__ = "object_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)


class Detection(Base):
    __tablename__ = "detection"
    id: Mapped[int] = mapped_column(primary_key=True)

    image_id: Mapped[int] = mapped_column(ForeignKey("image.id"))
    image: Mapped["Image"] = relationship(back_populates="detection")

    object_id: Mapped[int] = mapped_column(ForeignKey("object_type.id"), nullable=False)
    object: Mapped["ObjectType"] = relationship(back_populates="detection")

    y_min: Mapped[float] = mapped_column(Float, nullable=False)
    y_max: Mapped[float] = mapped_column(Float, nullable=False)
    x_min: Mapped[float] = mapped_column(Float, nullable=False)
    x_max: Mapped[float] = mapped_column(Float, nullable=False)

    confidenc: Mapped[float] = mapped_column(Float, nullable=False)
