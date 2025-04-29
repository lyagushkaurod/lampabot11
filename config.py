import os

from aiogram import Dispatcher, Bot
from dotenv import load_dotenv

load_dotenv()


bot = Bot(os.getenv('TOKEN'))
SUPPORT_CHAT_ID = int(os.getenv('SUPPORT_CHAT_ID'))
dp = Dispatcher()
