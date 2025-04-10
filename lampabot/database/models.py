from sqlalchemy import String, Date, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import re

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Bron(Base):
    __tablename__ = 'bron'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[int]
    place: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[Date] = mapped_column(Date, server_default=func.current_date())
    time: Mapped[time] = mapped_column(DateTime)


