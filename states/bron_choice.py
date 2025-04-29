from aiogram.fsm.state import StatesGroup, State


class bron_choice(StatesGroup):
    place = State()
    name = State()
    pupils = State()
    pupilsplus = State()
    minkoms = State()
    username = State()
    date = State()
    time = State()
    timeout = State()
    waiting_hours = State()
    phone_number = State()
    contact_method = State()