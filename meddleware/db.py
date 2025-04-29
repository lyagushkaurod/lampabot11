from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from sqlalchemy.ext.asyncio import async_sessionmaker
from database.engine import async_session


class CounterMiddleware(BaseMiddleware):
     def __init__(self) -> None:
         self.counter = 0

     async def __call__(
         self,
         handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
         event: TelegramObject,
         data: Dict[str, Any]
     ) -> Any:
         self.counter += 1
         data['counter'] = self.counter
         return await handler(event, data)


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(self, handler, event, data):
        async with self.session_pool() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e