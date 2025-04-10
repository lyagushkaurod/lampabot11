from operator import truediv

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from telebot.types import ReplyKeyboardRemove

start_bro = ReplyKeyboardBuilder()
start_bro.add(
    KeyboardButton(text="Забронировать")
)


start_kb = ReplyKeyboardBuilder()
start_kb.attach(start_bro)
start_kb.row(KeyboardButton(text="О нас"))

back_bt = ReplyKeyboardBuilder()
back_bt.add(KeyboardButton(text='Назад'))



bron_kb = ReplyKeyboardBuilder()
bron_kb.row(KeyboardButton(text='Приватный зал'))
bron_kb.row(KeyboardButton(text='Столик(общий зал)'))
bron_kb.row(KeyboardButton(text='Консоль'))
bron_kb.row(KeyboardButton(text='ПК'))


console_kb = ReplyKeyboardBuilder()
console_kb.row(
    KeyboardButton(text='PlayStation 4'),
    KeyboardButton(text='PlayStation 5'),
)
console_kb.row(
    KeyboardButton(text='PlayStation 4 с VR-шлемом')
)
console_kb.attach(back_bt)

privat_kb = ReplyKeyboardBuilder()
privat_kb.row(
    KeyboardButton(text='До 10'),
    KeyboardButton(text='10-13'),
)
privat_kb.row(
    KeyboardButton(text='13-16'),
    KeyboardButton(text='16-20'),
)
privat_kb.attach(back_bt)


oukey_kb = ReplyKeyboardBuilder()
oukey_kb.add(KeyboardButton(text='Мне подходит'))
oukey_kb.attach(back_bt)


