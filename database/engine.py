import os
import sqlite3

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import date, datetime, time
import datetime
from database.models import Base, Bron
import gspread
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from oauth2client.service_account import ServiceAccountCredentials


def sqlite_adapter():
    def adapt_date(date_val):
        return date_val.isoformat()
    
    def adapt_time(time_val):
        return time_val.isoformat()
    
    # Регистрируем адаптеры
    sqlite3.register_adapter(date, adapt_date)
    sqlite3.register_adapter(time, adapt_time)

engine = create_async_engine(os.getenv('DB_LITE'), echo=True)
sqlite_adapter()

async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 1. Подключение к SQLite
def init_connections():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("burnished-ray-456812-r2-ee2f44ae34cd.json", scope)
    client = gspread.authorize(creds)
    
    # 3. Открытие таблицы
    spreadsheet = client.open_by_key("1Yn-9dRLMq5QKqQ97rQpXvcIIpL4rul4WPVOdwNf_SwA")
    worksheet = spreadsheet.worksheet("Лист1")
    
    return engine, worksheet




async def export_to_sheets(engine, worksheet):
    async with AsyncSession(engine) as session:
        stmt = select(Bron)
        result = await session.execute(stmt)
        records = result.scalars().all()
        
        headers = ["ID", "Ник ТГ", "Имя", "Телефон", "Место", "Дата", "Время", "Время ухода", "Филиал", "Кол-во человек", "Способ связи"]
        data = [headers]
        
        for record in records:
            row = [
                record.id,
                record.username,
                record.name,
                record.phone_number,
                record.place,
                record.date.strftime("%Y-%m-%d"),
                record.time.strftime("%H:%M:%S") if record.time else "00:00:00",
                record.timeout.strftime("%H:%M:%S") if record.timeout else "00:00:00",
                record.minkoms,
                record.pupils,
                record.contact_method
            ]
            data.append(row)
        
        worksheet.clear()
        worksheet.update(range_name="A1", values=data)
        print("Данные успешно экспортированы!")
