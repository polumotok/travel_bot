import json
from datetime import date
from typing import Any
from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar
from handlers.custom_handlers import user_class
from loader import bot
from config_data.config import SERCH_COMMANDS, command, command_text, FOTO_COMMAND, foto

"""
Основной модуль программы телеграмм-бота.
Содержит функции, отвечающие за взаимодействие бота с пользователем:
обработка команд;
обработка нажатия кнопки.
"""



@bot.message_handler(commands=['start'])
def start(message):
    """
    Обрабатывает команды типа '/start' и запрашивает на какую дату искать отель.
    """
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(message.chat.id,
                     "Укажите на какую дату искать отель?",
                     reply_markup=calendar)
@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar(min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text("Укажите на какую дату искать отель?",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Выбрана дата {result}",
                              c.message.chat.id,
                              c.message.message_id)
        # bot.send_message(c.message.chat.id,'Укажите параметры поиска')
        # text = [f"/{command} - {desk}" for command, desk in SERCH_COMMANDS]
        # bot.send_message(c.message.chat.id, "\n".join(text))
        bot.send_message(c.message.chat.id, 'Выводить фото?')
        text = [f"/{command} - {desk}" for command, desk in FOTO_COMMAND]
        bot.send_message(c.message.chat.id, "\n".join(text))
        with open('serch_date.json', 'w', encoding='utf-8') as f:
            json.dump(str(result).split("-"), f)

@bot.message_handler(commands=foto)
def view_foto(message):
    msg = message.text
    bot.send_message(message.chat.id,'Укажите параметры поиска')
    text = [f"/{command} - {desk}" for command, desk in SERCH_COMMANDS]
    bot.send_message(message.chat.id, "\n".join(text))
    with open('foto.json', 'w', encoding='utf-8') as f:
        json.dump(str(msg), f)
users = dict()

@bot.message_handler(commands=command)
def serch_func(message: Message):
    """
    Обрабатывает команды типа '/text'
    """
    users[f"{message.chat.id}"] = [message.from_user.first_name, message.from_user.last_name]
    text = ', Давайте определимся с местом отдыха.\nВведите название города\n(Enter the name of the city): '
    if message.text[1::] in command:
        letter = message.text[1]
        bot.send_message(message.from_user.id, str(message.from_user.first_name) + text)
        bot.register_next_step_handler(message, user_class.User(message.chat.id, bot, command_text).city_search,
                                           str(letter).lower())



@bot.callback_query_handler(func=lambda call: True)
def handle(call) -> Any:
    """
    Обработка кнопок. Информация имеет вид: 'cityP1234567l' P-для выбора языка, l -откуда пришла,
    city - подтверждает выбор пользователем города, передаёт  'P1234567l' и новый message в
    num_for_text для проверки нового message на числовое значение
    """

    city_id = call.data
    text = user_class.translate_eng(city_id, 'Какое количество отелей вывести?')
    bot.send_message(call.message.chat.id, text)
    users[f"{call.message.chat.id}"].append(city_id)

    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(users, f)
    bot.register_next_step_handler(call.message, user_class.User(call.message.chat.id, bot,
                                                                 command_text).num_for_text, city_id)



