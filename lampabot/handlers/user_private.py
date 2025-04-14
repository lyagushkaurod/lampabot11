from aiogram import types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InputFile, FSInputFile, Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, session

from database.models import Bron
from database.orm_querry import orm_bron, orm_bron
from keyboards import reply
from keyboards.inline import get_callback_btns


user_router = Router()

class bron_choice(StatesGroup):
    place = State()
    name = State()
    date = State()
    time = State()
    phone_number = State()




#кнопка старт
@user_router.message(CommandStart())
async def start(message: types.Message):
    with open('hello.txt', 'r', encoding='utf-8') as file:
        hello = file.read()
    await message.answer(text=hello,
                         reply_markup=get_callback_btns(
                             btns={"Тарифы": f'abtus',
                                   "Забронировать": f'bronstart'},
                         ))

#кнопка о нас, при нажатии выдает информацию из about_us.txt
@user_router.callback_query(F.data == 'abtus')
async def abt(callback: types.CallbackQuery):
    with open('about_us.txt', 'r', encoding='utf-8') as file:
        abt_txt = file.read()
    await callback.message.answer(abt_txt,
                                  reply_markup=get_callback_btns(
                                      btns={"Забронировать": f'bronstart'}
                                  ))

#кнопка забронировать
@user_router.callback_query(F.data == 'bronstart')
async def bron(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Конечно! За чем вы бы хотели провести время?',
                         reply_markup=get_callback_btns(
                             btns={"Приватный зал": f'privat',
                                   "Консоль": f'console',
                                   "Стол": f'stol',
                                   "ПК": f'pc'}
                         ))

    await state.set_state(bron_choice.place)

#кнопка назад
@user_router.callback_query(F.data == 'abt')
async def back(callback: types.CallbackQuery, state:FSMContext):
    currentstate = await state.get_state()
    if currentstate == bron_choice.choice:
        await callback.message.answer('Предыдущего шага не было.')
    previous = None
    for step in bron_choice.__all_states__:
        if step.state == currentstate:
            await state.set_state(previous)
            return


#выбор консоли
@user_router.callback_query(F.data == 'console')
async def cons(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('За какой консолью тебе хотелось бы посидеть?',
                         reply_markup=get_callback_btns(
                             btns={"PlayStation5": f'ps5',
                                   "PlayStation 4": f'ps4',
                                   "PlayStation 4 с VR-шлемом": f'vr',
                                   }
                         ))
    await state.set_state(bron_choice.place)

@user_router.callback_query(F.data == 'ps5')
async def ps5(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer('Отличный выбор!',
                         reply_markup=reply.oukey_kb.as_markup(
                             resize_keyboard=True,
                             input_field_placeholder='Подтвердите свой выбор'
                         ))
    await state.set_state(bron_choice.name)

@user_router.callback_query(F.data == 'privat')
async def privat(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Сколько человек планируется?',
                                  reply_markup=get_callback_btns(
                                      btns={"До 10": f'fiol',
                                            "До 13": f'green',
                                            "До 16": f'redkoms',
                                            "Свыше 16": f'redmin'},
                                            sizes = (2, 2)
                                            ))



@user_router.callback_query(F.data == 'fiol')
async def fiol(callback: types.CallbackQuery, state: FSMContext):
    photof = FSInputFile('pictures/fiol.png')
    with open('fiol.txt', 'r', encoding='utf-8') as file:
        violet = file.read()
    await callback.message.answer_photo(photo=photof,caption=violet,
                                        reply_markup=get_callback_btns(
                                            btns={"Мне подходит": f'gotoname',
                                                  }
                                        ))

@user_router.callback_query(F.data == 'green')
async def green(callback: types.CallbackQuery, state: FSMContext):
    photog = FSInputFile('pictures/green.jpg')
    with open('green.txt', 'r', encoding='utf-8') as file:
        green = file.read()
    await callback.message.answer_photo(photo=photog,caption=green,
                                        reply_markup=get_callback_btns(
                                            btns={"Мне подходит": f'gotoname',
                                                  }
                                        ))

@user_router.callback_query(F.data == 'redkoms')
async def redkoms(callback: types.CallbackQuery, state: FSMContext):
    photork = FSInputFile('pictures/redkoms.jpg')
    with open('redkoms.txt', 'r', encoding='utf-8') as file:
        redkoms = file.read()
    await callback.message.answer_photo(photo=photork, caption=redkoms,
                                        reply_markup=get_callback_btns(
                                            btns={"Мне подходит": f'gotoname',
                                                    }
                                        ))

    await orm_bron(session, place="Кирпичный зал")
    await state.set_state(name)


@user_router.callback_query(F.data == 'redmin')
async def redmin(callback: types.CallbackQuery, state: FSMContext):
    photorm = FSInputFile('pictures/redmin.jpg')
    with open('redmin.txt', 'r', encoding='utf-8') as file:
        redmin = file.read()
    await callback.message.answer_photo(photo=photorm, caption=redmin,
                                        reply_markup=get_callback_btns(
                                            btns={"Мне подходит": f'gotoname',
                                                    }
                                        ))

@user_router.callback_query(F.data == 'stol')
async def stol(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(' Отличный выбор!',
                                  reply_markup=get_callback_btns(
                                      btns={"Мне подходит": f'gotoname'
                                            }))
    await state.set_state(bron_choice.date)

@user_router.callback_query(F.data == 'gotoname')
async def name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Как к вам можно обращаться?')
    await state.set_state(bron_choice.name)
    await callback.answer()

@user_router.message(bron_choice.name, F.text)
async def process_name(message: Message, state: FSMContext):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(user_id=message.from_user.id)
            session.add(user)
        
        user.name = message.text
        await session.commit()
    
    await message.answer(f"Хорошо, {message.text}! В какой день вы хотите прийти? Укажите дату в формате ДД.ММ")
    await state.set_state(bron_choice.date) 

@user_router.message(BronChoice.date, F.text)
async def process_date(message: Message, state: FSMContext):
    try:
        input_date = datetime.strptime(message.text, "%d.%m")
        current_year = datetime.now().year
        full_date = input_date.replace(year=current_year).date()

        async with async_session() as session:
            user = await session.get(User, message.from_user.id)
            if user:
                user.date = full_date
                await session.commit()
                await message.answer(
                    f"Дата {full_date.strftime('%d.%m.%Y')} успешно сохранена!\n"
                    f"Ваше имя: {user.name}\n"
                    f"Ваша дата: {full_date.strftime('%d.%m.%Y')}"
                )
                await state.clear()
            else:
                await message.answer("Сначала нужно указать имя!")
                await state.clear()

    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте еще раз в формате ДД.ММ (например 25.12)")
    except Exception as e:
        await message.answer("Произошла ошибка. Попробуйте еще раз.")
        await state.clear()
        print(f"Error: {e}")

@user_router.message(bron_choice.time, F.text)
async def process_time(message: Message, state: FSMContext):
    try:
        input_time = datetime.strptime(message.text, "%H:%M").time()
        async with async_session() as session:
            user = await session.get(User, message.from_user.id)
            if user:
                user.time = input_time
                await session.commit()
                await message.answer(
                    "Выберите способ ввода номера:",
                    reply_markup=get_callback_btns(
                        btns={
                            "Отправить номер телефона": "sendnumber",
                            "Ввести номер вручную": "typenumber"
                        },
                        sizes=(2,)
                    )  
                )  
                
                await state.set_state(bron_choice.phone_number)
            else:
                await message.answer("❌ Сначала укажите имя и дату!")
                await state.clear()
                
    except ValueError:
        await message.answer("⚠️ Неверный формат времени. Используйте ЧЧ:MM (например 14:30)")


@user_router.callback_query(Text("sendnumber"))
async def send_phone_handler(callback: CallbackQuery, state: FSMContext):
    try:
        async with async_session() as session:
            user = await session.get(User, callback.from_user.id)
            if user:
                # Пытаемся получить номер из профиля Telegram
                if callback.from_user.phone_number:
                    user.phone_number = callback.from_user.phone_number
                    await session.commit()
                    await callback.message.edit_text(
                        f"✅ Номер {callback.from_user.phone_number} успешно сохранен!\n"
                        f"▫️ Имя: {user.name}\n"
                        f"▫️ Дата: {user.date.strftime('%d.%m.%Y')}\n"
                        f"▫️ Время: {user.time.strftime('%H:%M')}\n"
                        f"▫️ Телефон: {callback.from_user.phone_number}"
                    )
                else:
                    await callback.message.answer("❌ Номер не привязан к вашему аккаунту Telegram")
                    await state.set_state(bron_choice.phone_number)
            else:
                await callback.message.answer("❌ Сначала заполните предыдущие данные!")
            
            await state.clear()
            await callback.answer()

    except Exception as e:
        print(f"Error: {e}")
        await callback.message.answer("⚠️ Произошла ошибка при обработке номера")

@user_router.callback_query(Text("typenumber"))
async def type_phone_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📱 Введите номер в формате +7XXXXXXXXXX:")
    await state.set_state(bron_choice.phone_number)
    await callback.answer()              

