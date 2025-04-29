import asyncio
import os

import gspread
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from dotenv import find_dotenv, load_dotenv
from config import bot, SUPPORT_CHAT_ID, dp
from handlers.group import user_group_router

load_dotenv(find_dotenv())

from database.engine import export_to_sheets, init_connections

from database.engine import engine
from database.engine import async_session, drop_db, create_db
from handlers.user_private import user_router
from meddleware.db import CounterMiddleware, DataBaseSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler



engine, worksheet = init_connections()



bot.my_admins_list = []
storage = MemoryStorage()

allowed = ['message, callback_query, inline_query']

dp.include_router(user_router)
dp.include_router(user_group_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    await create_db()


    scheduler = AsyncIOScheduler()
    scheduler.add_job(export_to_sheets, 'interval', minutes=1, args=(engine, worksheet))
    scheduler.start()

async def on_shutdown(bot):
    print('Бот выключен')
    await export_to_sheets(engine, worksheet)

async def main():

    dp.update.middleware(DataBaseSession(session_pool=async_session))
    

    user_router.message.middleware(CounterMiddleware())  
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())
