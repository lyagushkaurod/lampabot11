
from aiogram import types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InputFile, FSInputFile, Message, TelegramObject, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession, session  
from database.models import Bron
from database.orm_querry import orm_bron, orm_bron
from database.requests import add_user
from handlers.functions import SupportRequest
from keyboards.inline import get_callback_btns
from keyboards.reply import get_keyboard
from config import SUPPORT_CHAT_ID, dp
from meddleware.validatenumber import is_valid_working_time, string_to_int, validate_date, validate_phone_number, format_time
from datetime import datetime, time, date, timedelta

from states.SupportState import SupportState
from states.bron_choice import bron_choice


user_router = Router()


@user_router.message(CommandStart())
async def start(message: types.Message, session: AsyncSession):  # Добавляем параметр session
    with open('hello.txt', 'r', encoding='utf-8') as file:
        hello = file.read()

    await message.answer(
        text=hello,
        reply_markup=get_callback_btns(
            btns={
                "Тарифы": "abtus",
                "Забронировать": "bronstart",
                "Связаться с оператором": "support"
            }
        )
    )

    await add_user(
        session=session,  # Передаем сессию явно
        tg_id=message.from_user.id,  # Убираем str(), если tg_id в БД число
        username=message.from_user.username,
        name=message.from_user.first_name
    )

#кнопка о нас, при нажатии выдает информацию из about_us.txt
@user_router.callback_query(F.data == 'abtus')
async def abt(callback: types.CallbackQuery):
    with open('about_us.txt', 'r', encoding='utf-8') as file:
        abt_txt = file.read()
    await callback.message.answer(abt_txt,
                                  reply_markup=get_callback_btns(
                                      btns={"Забронировать": f'bronstart'}
                                  ))


@user_router.callback_query(F.data == 'support')
async def send_request(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    support_request = SupportRequest(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        message_id=callback.message.message_id,  # Правильное получение ID сообщения
    )

    await support_request.send_support_request()
    await callback.message.reply(text="Ваше сообщение отправлено. Ожидайте ответа.")
    await state.clear()




@user_router.message(
    SupportState.in_support,
    F.content_type.in_({'any'})
)
async def support_reply(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    message_thread_id = state_data.get("message_thread_id")
    await dp.bot.forward_message(
        from_chat_id=message.chat.id,
        message_thread_id=message_thread_id,
        chat_id=SUPPORT_CHAT_ID,
        message_id=message.message_id,
    )

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

#ps5
@user_router.callback_query(F.data == 'ps5')
async def ps5(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer('Отличный выбор! Со списком игр установленных на консоли можете ознакомиться по ссылке.  ',
                        reply_markup=get_callback_btns(
                                            btns={"Мне подходит": f'gotopupils',
                                                  }))
    await state.update_data(place="PS5")
    await state.set_state(bron_choice.pupils)

#ps4
@user_router.callback_query(F.data == 'ps4')
async def ps5(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer('Отличный выбор! Со списком игр установленных на консоли можете ознакомиться по ссылке. ',
                        reply_markup=get_callback_btns(
                                            btns={"Мне подходит": f'gotopupils',
                                                  }))
    await state.update_data(place="PS4")
    await state.set_state(bron_choice.pupils)

#vr
@user_router.callback_query(F.data == 'vr')
async def ps5(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.answer('Отличный выбор! Со списком игр установленных на консоли можете ознакомиться по ссылке. \n' 
    'VR присутствует только на Минской,67\n' 
    'Рекомендуемое воличество человек до 8', reply_markup=get_callback_btns(
                                            btns={"Мне подходит": f'gotopupilsplus',
                                                  }))
    await state.update_data(place="VR")
    await state.set_state(bron_choice.pupilsplus)

#стол
@user_router.callback_query(F.data == 'stol')
async def stol(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(' Отличный выбор!',
                                  reply_markup=get_callback_btns(
                                      btns={"Мне подходит": f'gotopupils'
                                            }))
    await state.update_data(place="Стол")
    await state.set_state(bron_choice.pupils)  

#pc
@user_router.callback_query(F.data == 'pc')
async def stol(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Отличный выбор!\n'
                                  'Компьютеры присутствует только на Минской,67\n'
                                  'Количество компьютеров: 4',
                                  reply_markup=get_callback_btns(
                                      btns={"Мне подходит": f'gotopupilsplus'

                                            }))
    await state.update_data(place="PC")
    await state.set_state(bron_choice.pupilsplus)  



@user_router.callback_query(F.data == "gotopupils")
async def pupulsstart(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Сколько вас планируется человек?')
    await callback.answer()


@user_router.message(bron_choice.pupils, F.text)
async def pupils(message: Message, state: FSMContext):
    colvo = string_to_int(message.text)
    if colvo == None:
        await message.answer('Введите число')
    elif colvo > 10:
       await message.answer('Максимальное количество человек для мест в общем зале: 10.\n'
                             'Введите количество меньше или забронируйте приватный зал', reply_markup=get_callback_btns(
                                 btns={
                                     "Перейти к выбору залов": f'privat'
                                 }
                             ))
    else:
        await state.update_data(pupils=message.text)
        await state.set_state(bron_choice.minkoms)
        await message.answer('Давайте продолжим', reply_markup=get_callback_btns(
            btns={
                "Перейи к выбору филиала": f'gotominkoms'
            }
        ))

#для пк и vr
@user_router.callback_query(F.data == "gotopupilsplus")
async def pupulsplusstart(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Сколько вас планируется человек?')
    await callback.answer()


@user_router.message(bron_choice.pupilsplus, F.text)
async def pupilsplus(message: Message, state: FSMContext):
    colvo = string_to_int(message.text)
    if colvo == None:
        await message.answer('Введите число')
    elif colvo > 10:
        await message.answer('Максимальное количество человек для мест в общем зале:10.\n'
                             'Введите количество меньше или забронируйте приватный зал', 
                             reply_markup=get_callback_btns(
                                 btns={
                                     "Перейти к выбору залов": f'privat'
                                 }
                             ))
    else:
        await state.update_data(pupils=message.text)
        await state.update_data(minkoms="Минская 67")
        await message.answer('Давайте продолжим', reply_markup=get_callback_btns(
            btns={
                "Продолжить": f'gotoname'
            }
        ))
        await state.set_state(bron_choice.name)


#выбор филиала
@user_router.callback_query(F.data == 'gotominkoms')
async def filial(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Какой филиал для вас будет удобнее?',
                                  reply_markup=get_callback_btns(
                                      btns={"Минская, 67": f'min',
                                            "Комсомольская, 8": f'koms'
                                            }))

@user_router.callback_query(F.data == 'min')
async def min(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(minkoms='Минская 67')
    await callback.message.answer(f'Запомнил, вам удобнее Минская', reply_markup=get_callback_btns(
        btns={
            "Продолжить": f'gotoname'
        }
    ))
    await state.set_state(bron_choice.name)

@user_router.callback_query(F.data == 'koms')
async def min(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(minkoms='Комсомольская 8')
    await callback.message.answer(f'Запомнил, вам удобнее Комсомольская', reply_markup=get_callback_btns(
        btns={
            "Продолжить": f'gotoname'
        }
    ))
    await state.set_state(bron_choice.name)
    

#переход на приватные залы
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


#фиолетовый
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
    await state.update_data(place="Фиолетовый зал")
    await state.update_data(minkoms="Минская 67")
    await state.set_state(bron_choice.name)

#зеленый
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
    await state.update_data(place="Зеленый зал")
    await state.update_data(minkoms='Комсомольская 8')
    await state.set_state(bron_choice.name)

#кирпичный
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

    await state.update_data(place="Кирпичный зал")
    await state.update_data(minkoms='Комсомольская 8')
    await state.set_state(bron_choice.name)  

#красный
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
    await state.update_data(place="Красный зал")
    await state.update_data(minkoms="Минская 67")
    await state.set_state(bron_choice.name)  



#просьба указать имя
@user_router.callback_query(F.data == 'gotoname')
async def name(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Как к вам можно обращаться?')
    await state.set_state(bron_choice.name)
    await callback.answer()

#приемка имени, просьба указания телефона
@user_router.message(bron_choice.name, F.text)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    await message.answer(
    f"Хорошо, {message.text}! Для связи с вами в случае проблем с бронированием, "
    "напишите свой номер телефона в формате +7XXXXXXXXXX или нажмите на кнопку",
    reply_markup=get_keyboard("Отсправить номер", request_contact=1))
    await state.set_state(bron_choice.phone_number) 


#приемка телефона->дата
@user_router.message(bron_choice.phone_number, F.text | F.contact)
async def getnumber(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        elif not phone.startswith('+7'):
            phone = '+7' + phone
        else:
            phone = message.text
    if validate_phone_number(phone):
        await message.answer(
            "Номер принят, осталось определиться с датой. "
            "Укажите дату когда вы бы хотели прийти в формате ДД.ММ", reply_markup=ReplyKeyboardRemove()
        )
        await state.update_data(phone_number=phone)
        await state.set_state(bron_choice.date)
    else:
        await message.answer(
            "Неверный формат номера, попробуйте еще раз!\n"
            "Пример правильного формата: +79123456789\n"
            "Или используйте кнопку для отправки контакта 📱"
        )




#приемка даты->время
@user_router.message(bron_choice.date, F.text)
async def process_date(message: types.Message, state: FSMContext):
    try:

        date_str = message.text  
        input_date = datetime.strptime(date_str, "%d.%m").date()
        await state.update_data(date=input_date)
        await message.answer("🕒 Теперь введите время (формат ЧЧ:ММ):")
        await state.set_state(bron_choice.time)
    except ValueError:
        await message.answer("❌ Неверный формат даты! Используйте ДД.ММ")





@user_router.message(bron_choice.time, F.text)
async def process_time(message: types.Message, state: FSMContext):
    try:
        # Парсим время и сохраняем как объект datetime.time
        input_time = datetime.strptime(message.text, "%H:%M").time()
        
        if time(3, 0) <= input_time < time(12, 0):
            await message.answer("⏰ Мы не работаем в это время!")
            return
            
        await state.update_data(time=input_time)
        await message.answer(
            "✅ Время сохранено! Выберите продолжительность", 
            reply_markup=get_callback_btns(
                btns={
                    "До 2 часов": f'upto2',
                    "2-4 часа": f'upto4',
                    "Более 4 часов(указать время)": f'more4'
                }
            )
        )

    except ValueError:
        await message.answer("❌ Неверный формат! Используйте ЧЧ:ММ (например: 14:30)")
    except Exception as e:
        print(f"Time processing error: {e}")
        await message.answer("❌ Ошибка обработки времени")
                        
# Хендлер для 2 часов (исправленный)
@user_router.callback_query(F.data == 'upto2')
async def handle_upto2(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        
        # Проверяем тип данных
        if not isinstance(data.get('time'), time):
            raise TypeError("Неверный тип данных времени")
            
        start_time = data['time']
        
        # Создаем полный объект datetime
        end_datetime = datetime.combine(
            date.today(),  # текущая дата
            start_time     # объект времени
        ) + timedelta(hours=2)
        
        # Извлекаем только время
        end_time = end_datetime.time()
        
        if not (end_time >= time(12, 0) or end_time < time(3, 0)):
            await callback.message.answer("❌ Время окончания вне рабочего периода!")
            return
            
        await state.update_data(timeout=end_time)
        await show_contact_choice(callback.message)
        await state.set_state(bron_choice.contact_method)
        await callback.answer()

    except KeyError:
        await callback.message.answer("❌ Время бронирования не найдено!")
    except TypeError as e:
        print(f"Type error: {str(e)}")
        await callback.message.answer("❌ Ошибка в данных времени")
    except Exception as e:
        print(f"Error: {str(e)}")
        await callback.message.answer("❌ Ошибка обработки запроса")

# Хендлер для 4 часов
@user_router.callback_query(F.data == 'upto4')
async def handle_upto4(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        start_time = data['time']
        
        end_datetime = datetime.combine(
            date.today(),
            start_time
        ) + timedelta(hours=4)
        
        end_time = end_datetime.time()
        
        if not is_valid_working_time(end_time):
            await callback.message.answer("❌ Время окончания вне рабочих часов (12:00-03:00)!")
            return
            
        await state.update_data(timeout=end_time)
        await show_contact_choice(callback.message)
        await state.set_state(bron_choice.contact_method)
        await callback.answer()

    except KeyError:
        await callback.message.answer("❌ Ошибка: время бронирования не найдено!")
        await callback.answer()
    except Exception as e:
        await callback.message.answer("❌ Ошибка обработки запроса")
        print(f"Error in upto4: {str(e)}")
        await callback.answer()

# Хендлер для ручного ввода
@user_router.callback_query(F.data == "more4")
async def handle_more4(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.answer("⌛ Введите количество часов (от 5 до 8):")
        await state.set_state(bron_choice.waiting_hours)
        await callback.answer()
    except Exception as e:
        print(f"Error in more4: {str(e)}")
        await callback.answer()

# Хендлер для ручного ввода часов
from datetime import datetime, date, time, timedelta

@user_router.message(bron_choice.waiting_hours, F.text)
async def process_custom_hours(message: types.Message, state: FSMContext):
    try:

        duration = int(message.text)
        if not 5 <= duration <= 8:
            raise ValueError("Допустимый диапазон: 5-8 часов")

        data = await state.get_data()
        start_time = data.get('time')
        
        if not isinstance(start_time, time):
            raise TypeError(f"Ожидается объект time, получен {type(start_time)}")

        start_datetime = datetime.combine(
            date.today(),   
            start_time       
        )
        end_datetime = start_datetime + timedelta(hours=duration)
        end_time = end_datetime.time()


        if not is_valid_working_time(end_time):
            await message.answer("❌ Время окончания должно быть между 12:00 и 03:00!")
            return

        await state.update_data(timeout=end_time)
        await show_contact_choice(message)
        await state.set_state(bron_choice.contact_method)

    except ValueError as ve:
        await message.answer(f"❌ {str(ve)}")
    except TypeError as te:
        print(f"TypeError: {str(te)}")
        await message.answer("❌ Ошибка формата времени! Начните бронирование заново.")
        await state.clear()
    except Exception as e:
        await message.answer("❌ Критическая ошибка! Попробуйте позже.")
        print(f"Unhandled error: {str(e)}")

# Общий метод для показа выбора связи
async def show_contact_choice(msg: types.Message):
    await msg.answer(
        "✅ Время подтверждено!\nВыберите способ связи:",
        reply_markup=get_callback_btns(btns={
            "📲 Telegram": "telegram",
            "📞 Телефон": "phone"
        })
    )

# Финализатор бронирования
@user_router.callback_query(F.data.in_(["telegram", "phone"]), bron_choice.contact_method)
async def finalize_booking(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        data = await state.get_data()
        if not all([
            isinstance(data['date'], date),
            isinstance(data['time'], time),
            isinstance(data['timeout'], time)
        ]):
            raise TypeError("Некорректные типы данных")
        print(f"Date type: {type(data['date'])}")  
        print(f"Time type: {type(data['time'])}")    
        print(f"Timeout type: {type(data['timeout'])}")  
        await orm_bron(
            session=session,
            time=data['time'],       
            timeout=data['timeout'], 
            date=data['date'],       
            place=data['place'],
            minkoms=data['minkoms'],
            username=callback.from_user.username,
            name=data['name'],
            phone_number=data['phone_number'],
            pupils=data['pupils'],
            contact_method=callback.data
        )
        await callback.message.answer(
            "✅ Бронь создана!\n"
            f"· Дата: {data['date'].strftime('%d.%m.%Y')}\n"
            f"· Время: {data['time'].strftime('%H:%M')}-{data['timeout'].strftime('%H:%M')}\n"
            f"· Адрес: {data['minkoms']}\n"
            f"· Место: {data['place']}\n"
            f"· Гостей: {data['pupils']}\n"
            f"· Связь: {'Telegram' if callback.data == 'telegram' else 'Телефон'}"
        )
    except TypeError as e:
        print(f"Type Error: {e}")
        await callback.message.answer("❌ Ошибка в данных бронирования")
    except Exception as e:
        print(f"DB Error: {repr(e)}")
         
