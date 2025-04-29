from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import CallbackQuery
from aiogram import types
from database.models import Users

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def add_user(
        session: AsyncSession,
        tg_id: int,
        username: str,
        name: str
):
    query = select(Users.id).where(Users.tg_id == tg_id)
    result = await session.execute(query)
    is_exists = result.scalar_one_or_none()

    if is_exists:
        return False

    user = Users(
        tg_id=tg_id,
        username=username,
        name=name
    )
    session.add(user)
    await session.commit()
    return user

async def get_users(session: AsyncSession):
    users = await session.execute(
        select(Users.tg_id)
    )
    return users.scalars().all()


async def preview(message: types.Message, data: dict):
    text = data.get("desc", "")
    photo = data.get("photo")  # Теперь это строка (file_id)

    sent_message = await message.answer_photo(
        caption=text,
        photo=photo,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    return sent_message.message_id

async def cancelsend(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Рассылка отменена")
    await state.clear()
    await callback.answer()

async def sending(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.answer("Рассылка началась")
    await state.clear()
    await callback.answer()

    user_ids = await get_users(session)
    message_id = data.get('message_id')
    count = await sender