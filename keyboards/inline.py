from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (1,),):

        keyboard = InlineKeyboardBuilder()

        for text, value in btns.items():
            if '://' in value:
                keyboard.add(InlineKeyboardButton(text=text, url=value))
            else:
                keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

        return keyboard.adjust(*sizes).as_markup()

