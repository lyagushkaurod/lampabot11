import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from database.engine import session_maker, drop_db, create_db
from handlers.user_private import user_router
from meddleware.db import CounterMiddleware, DataBaseSession



bot = Bot(token=os.getenv('TOKEN'))
bot.my_admins_list = []

storage = MemoryStorage()
dp = Dispatcher()
allowed = ['message, callback_query, inline_query']

dp.include_router(user_router)


async def on_startup(bot):

    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await create_db()

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

asyncio.run(main())

user_router.message.middleware(CounterMiddleware)

