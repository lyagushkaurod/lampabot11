from aiogram.fsm.state import StatesGroup, State


class Groupsend(StatesGroup):
    desc = State()
    photo = State()
    message_id = State()
    confirm = State()