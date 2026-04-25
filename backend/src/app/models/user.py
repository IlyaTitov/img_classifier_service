from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .base import Base


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False)
    image: Mapped[List["Image"]] = relationship(back_populates="user")
