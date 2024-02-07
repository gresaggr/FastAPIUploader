import datetime
from typing import Optional

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    url=settings.db.url, echo=settings.db.echo
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    hashed_password: Mapped[str]

    created_at = mapped_column(DateTime(), default=lambda: datetime.datetime.utcnow())
    updated_at = mapped_column(
        DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    # files: Mapped[Optional[list["File"]]] = relationship(back_populates="user")

    def __str__(self):
        return f"#{self.id}, {self.username}"


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str]

    created_at = mapped_column(DateTime(), default=lambda: datetime.datetime.utcnow())
    updated_at = mapped_column(
        DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # user: Mapped["User"] = relationship(back_populates="user")

    def __str__(self):
        return f"#{self.id}, user: {self.user_id} {self.path}"
