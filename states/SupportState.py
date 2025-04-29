from aiogram.fsm.state import StatesGroup, State


class SupportState(StatesGroup):
    send_request = State()
    in_support = State()