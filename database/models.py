from typing import Type

from aiogram.fsm.state import StatesGroup
from sqlalchemy import String, Date, Time, func, DateTime, Column, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import re

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Bron(Base):
    __tablename__ = 'bron'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)  
    place: Mapped[str] = mapped_column(String(50), nullable=False)
    minkoms: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[Date] = mapped_column(Date, server_default=func.current_date())
    time: Mapped[Time] = mapped_column(Time)
    timeout: Mapped[Time] = mapped_column(Time)
    pupils: Mapped[str] = mapped_column(String(2))
    contact_method: Mapped[str] = mapped_column(String(15))



class Users(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[str] = mapped_column(String(32))
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)


class SupportTickets(Base):
    __tablename__ = 'support_tickets'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer)
    message_thread_id = Column(Integer)

    @classmethod
    def create_ticket(cls, tg_id: int, message_thread_id: int) -> None:
        session = Session()
        ticket = cls(tg_id=tg_id, message_thread_id=message_thread_id)
        session.add(ticket)
        session.commit()
        session.close()

    @classmethod
    def get_ticket_by_message_thread_id(cls, message_thread_id: int) -> Type['SupportTickets'] | None:
        session = Session()
        ticket = session.query(cls).filter_by(message_thread_id=message_thread_id).first()
        session.close()
        return ticket

    @classmethod
    def get_ticket_by_tg_id(cls, tg_id: int) -> Type['SupportTickets'] | None:
        session = Session()
        ticket = session.query(cls).filter_by(tg_id=tg_id).first()
        session.close()
        return ticket

    @classmethod
    def delete_ticket(cls, message_thread_id: int) -> None:
        session = Session()
        ticket = session.query(cls).filter_by(message_thread_id=message_thread_id).first()
        session.delete(ticket)
        session.commit()
        session.close()