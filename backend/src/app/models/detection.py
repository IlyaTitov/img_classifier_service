from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .base import Base


class ObjectType(Base):
    __tablename__ = "object_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    detections: Mapped[List["Detection"]] = relationship(back_populates="object_type")


class Detection(Base):
    __tablename__ = "detection"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    image_id: Mapped[int] = mapped_column(ForeignKey("image.id"))

    object_type_id: Mapped[int] = mapped_column(ForeignKey("object_type.id"))

    y_min: Mapped[float] = mapped_column(Float, nullable=False)
    y_max: Mapped[float] = mapped_column(Float, nullable=False)
    x_min: Mapped[float] = mapped_column(Float, nullable=False)
    x_max: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    image: Mapped["Image"] = relationship(back_populates="detections")
    object_type: Mapped["ObjectType"] = relationship(back_populates="detections")
