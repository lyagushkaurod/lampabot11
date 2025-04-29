from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

from database.models import SupportTickets
from config import SUPPORT_CHAT_ID, dp
from config import bot, SUPPORT_CHAT_ID  # Добавьте импорт бота


class SupportRequest(BaseModel):
    user_id: int
    username: str | None
    message_id: int

    async def send_support_request(self):
        try:
            message_thread_id = await self._create_forum_topic()
            if not message_thread_id:
                raise ValueError("Не удалось создать тему форума")

            builder = types.InlineKeyboardBuilder()
            builder.button(text="Закрыть тикет", callback_data="close_ticket")

            await bot.send_message(
                chat_id=SUPPORT_CHAT_ID,
                message_thread_id=message_thread_id,
                text=f"Новое обращение от @{self.username} (ID: {self.user_id})",
                reply_markup=builder.as_markup()
            )

            await bot.forward_message(
                chat_id=SUPPORT_CHAT_ID,
                message_thread_id=message_thread_id,
                from_chat_id=self.user_id,
                message_id=self.message_id,
            )

            SupportTickets().create_ticket(self.user_id, message_thread_id)

        except Exception as e:
            print(f"Ошибка при отправке запроса: {e}")

    async def _create_forum_topic(self):
        try:
            topic = await bot.create_forum_topic(
                chat_id=SUPPORT_CHAT_ID,
                name=f"Заявка от {self.username or self.user_id}",
            )
            return topic.message_thread_id
        except Exception as e:
            print(f"Ошибка создания темы: {e}")
            return None