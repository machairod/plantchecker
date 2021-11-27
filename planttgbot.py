import configparser
import json
import os
import requests
import telebot
import datetime
import random
from telebot import types

server = 'http://127.0.0.1:5000/'

path = os.path.dirname(__file__)
config = configparser.ConfigParser()

configfile = os.path.join(path, 'settings.ini')
config.read(configfile)

token = config['telegram']['bot-token']
bot = telebot.TeleBot(token)


def plant_card(plant_id, user_id):
    # клавиатура карточки растения
    card_markup = types.InlineKeyboardMarkup()
    list_btn = types.InlineKeyboardButton('Назад к списку', callback_data="list")
    water_btn = types.InlineKeyboardButton('Полить', callback_data="water-" + str(plant_id))
    fertile_btn = types.InlineKeyboardButton('Удобрить', callback_data="fertile-" + str(plant_id))
    delete_btn = types.InlineKeyboardButton('Удалить растение', callback_data="delete-" + str(plant_id))
    card_markup.add(water_btn, fertile_btn)
    card_markup.add(list_btn)
    card_markup.add(delete_btn)

    # запрос данных растения из базы
    plant_url = server + f"plants/{plant_id}?login={user_id}"
    response = requests.get(plant_url)
    plantcard = json.loads(response.json())

    # формирование текста карточки
    msg = f"{plantcard['plantname']}, вид: {plantcard['plantspec']}\n\n" \
          f"Следующая дата полива: {plantcard['next_water']}\n" \
          f"Следующая дата удобрения: {plantcard['next_fertile']}\n\n" \
          f"Яркость освещения: {plantcard['light']} из 3.\n" \
          f"Опрыскивание: " + ("рекомендуется" if plantcard["spraying"] == 1 else "не рекомендуется")

    bot.send_message(user_id, msg, reply_markup=card_markup)


def water_plant(plant_id, login, **kwargs):
    date = None
    plantname = None
    user_id = None
    if len(kwargs) > 0:
        plantname = kwargs.get('plantname')
        user_id = kwargs.get('user_id')

    # запрос из апи
    water_url = server + '/plants/water/'
    jdata = {'id': plant_id, 'login': login, 'name': plantname, 'user_id': user_id, 'date': date}
    jdata = json.dumps(jdata, ensure_ascii=False)
    response = requests.put(water_url, json=jdata)
    return response.text


def fertile_plant(plant_id, login, **kwargs):
    date = None
    plantname = None
    user_id = None
    if len(kwargs) > 0:
        plantname = kwargs.get('plantname')
        user_id = kwargs.get('user_id')

    # запрос из апи
    fertile_url = server + '/plants/fertile/'
    jdata = {'id': plant_id, 'login': login, 'name': plantname, 'user_id': user_id, 'date': date}
    jdata = json.dumps(jdata, ensure_ascii=False)
    response = requests.put(fertile_url, json=jdata)
    return response.text


def plant_type_list(message):
    user_id = message.chat.id
    plant_url = server + f"?login={user_id}"
    response = requests.get(plant_url)
    plantspec = (json.loads(response.json()))
    return plantspec


@bot.message_handler(commands=['start'])
def start_and_add_user(message):
    name = message.from_user.first_name if message.from_user.first_name is not None else message.from_user.username
    bot.send_message(message.chat.id, f'Привет, {name}, я бот для своевременного ухода за растениями.')


@bot.message_handler(commands=['plantlist'])
def get_plant_list(message):
    user_id = message.chat.id
    plant_url = server + f"plants/?login={user_id}"
    response = requests.get(plant_url)
    plantlist = json.loads(response.json())

    list_markup = types.InlineKeyboardMarkup()
    for i in plantlist:
        btn = types.InlineKeyboardButton(i, callback_data="card-" + str(plantlist[i]['id']) + "-" + str(user_id))
        list_markup.add(btn)

    bot.send_message(user_id, f'В вашем списке - {len(plantlist)} растений :', disable_notification=True,
                     reply_markup=list_markup)


@bot.message_handler(commands=['memento'])
def memento(message: telebot.types.Message):
    user_id = message.chat.id

    # запрос из апи
    memento_url = server + f'memento/?login={user_id}'
    response = requests.get(memento_url)
    mem_list = json.loads(response.json())

    water_msg = '*MEMENTO*\n*Растения, требующие полива:*\n'
    fertile_msg = '*Растения, требующие удобрения:*\n'
    end_msg = 'растений нет.'
    tomorrow = datetime.date.today() + datetime.timedelta(1)

    # списки растений с просроченной датой полива и удобрения
    water_mem = {x[1]: (x[0], x[2]) for x in mem_list if datetime.datetime.strptime(x[2], "%d-%m-%Y").date() < tomorrow}
    fertile_mem = {x[1]: (x[0], x[3]) for x in mem_list if
                   datetime.datetime.strptime(x[3], "%d-%m-%Y").date() < tomorrow}

    # cписок и строка коллбека для кнопки групповой обработки растений
    water_id = list(map(lambda x: str(water_mem[x][0]), water_mem))
    fertile_id = list(map(lambda x: str(fertile_mem[x][0]), fertile_mem))
    waterall = 'waterall-' + str(user_id) + '-' + ('-'.join(water_id))
    fertileall = 'fertileall-' + str(user_id) + '-' + ('-'.join(fertile_id))

    mem_markup = types.InlineKeyboardMarkup()
    fertile_btn = None
    water_btn = None

    # сообщение аглушка, если просроченных нет, иначе генерирование сообщения
    if len(water_mem) == 0:
        water_msg += end_msg
    else:
        for i in water_mem:
            water_msg += i + ' - полить ' + water_mem[i][1] + '\n'
        # клавиатура
        water_btn = types.InlineKeyboardButton('Пометить: все политы', callback_data=waterall)

    if len(fertile_mem) == 0:
        fertile_msg += end_msg
    else:
        for i in fertile_mem:
            fertile_msg += i + ' - удобрить ' + fertile_mem[i][1] + '\n'

        # клавиатура
        fertile_btn = types.InlineKeyboardButton('Пометить: все удобрены', callback_data=fertileall)

    if fertile_btn is not None:
        mem_markup.add(fertile_btn)
    if water_btn is not None:
        mem_markup.add(water_btn)

    mem_msg = water_msg + '\n\n' + fertile_msg
    bot.send_message(user_id, mem_msg, reply_markup=mem_markup, parse_mode='Markdown')


@bot.message_handler(commands=['addplant'])
def add_plant_step1(message: telebot.types.Message):
    bot.send_message(message.chat.id, "Нужно выбрать название растения. Например 'Кактус на кухне'",
                     reply_markup=telebot.types.ForceReply())


@bot.message_handler(content_types=['text'])
def reply_text(message: telebot.types.Message):
    if message.reply_to_message:
        # add plant step 2
        if "название растения" in message.reply_to_message.text:
            plantname = message.text.capitalize()
            bot.send_message(message.chat.id, f"Отлично, значит назовем его: {plantname}.\n\nТеперь нужно выбрать вид "
                                              f"растения. Набери первые 3-5 букв, чтобы я предложил варианты "
                                              "из своей базы. Осторожно, я не переживу грамматической ошибки)",
                             reply_markup=telebot.types.ForceReply())

        # add plant step 3
        elif "вид растения" in message.reply_to_message.text:
            user_id = message.chat.id
            plant_types = plant_type_list(message)
            plantname = message.reply_to_message.text
            start = plantname.find(':') + 2
            end = plantname.find(".")
            plantname = plantname[start:end]

            answer = message.text

            types_markup = types.InlineKeyboardMarkup()
            for i in plant_types:
                if answer in i:
                    msg = f"Ок, для '{answer}' я нашел такие варианты:"
                    btn = types.InlineKeyboardButton(i.capitalize(),
                                                     callback_data="type-" + plantname + "-" + i + "-" + str(user_id))
                    types_markup.add(btn)

            if 'btn' not in locals():
                plants = list(plant_types.keys())
                plant = [random.choice(plants) for i in range(3)]

                for i in plant:
                    btn = types.InlineKeyboardButton(i.capitalize(),
                                                     callback_data="type-" + plantname + "-" + i + "-" + str(user_id))
                    types_markup.add(btn)
                msg = f"Для '{answer}' я ничего не нашел. Так что выбери один из вариантов ниже, чтобы мы " \
                      f"могли продолжить: "

            choose_plant = bot.send_message(message.chat.id, msg,
                                            reply_markup=types_markup)

        # add plant step 4 and ending
        elif "растение последний раз поливали" in message.reply_to_message.text:
            answer = message.text

            if len(answer) == 10 and answer.count('-') == 2:
                water_date = answer
                bot.send_message(message.chat.id,
                                 f"Ок, значит растение последний раз поливали: {answer}\n\nХорошо, я собрал все "
                                 f"данные. Добавляю новый горшок в базу.")
            else:
                water_date = datetime.date.today()
                bot.send_message(message.chat.id,
                                 "Хорошо, значит растение последний раз поливали сегодня\n\nХорошо, я собрал все "
                                 "данные. Добавляю новый горшок в базу.")

            data = message.reply_to_message.text
            start = data.find('имя: ') + len('имя: ')
            stop = data.find(',')
            name = data[start:stop]

            start = data.find('вид: ') + len('вид: ')
            stop = data.find('.')
            plant_type = data[start:stop]

            add_plant_data = {'login': message.chat.id, 'plantname': name, 'plantspec': plant_type,
                              'last_watering': water_date}

            addplant_url = server + 'plants/'
            add_plant_data = json.dumps(add_plant_data, ensure_ascii=False)
            addplant = requests.post(addplant_url, json=add_plant_data)

        else:
            bot.send_message(message.chat.id, f"Что-то произошло, я не понял команду.", parse_mode="MARKDOWN")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: telebot.types.CallbackQuery):
    if call.message:
        if "card-" in call.data:
            carddata = call.data.split('-')
            user_id = carddata[2]
            plant_id = carddata[1]
            bot.delete_message(call.message.chat.id, call.message.message_id)
            plant_card(plant_id, user_id)

        # не добавляй гребанный дефис, чтобы опять все не уронить!!!!!
        if 'list' in call.data:
            message = call.message
            get_plant_list(message)
            bot.delete_message(call.message.chat.id, call.message.message_id)

        if 'water-' in call.data:
            water = call.data.split("-")
            plant_id = water[1]
            user_id = call.message.chat.id
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Растение полито")
            bot.delete_message(user_id, call.message.message_id)
            answer = water_plant(plant_id, user_id)
            if 'полито' in answer:
                bot.send_message(user_id, str(answer))
                plant_card(plant_id, user_id)
            else:
                bot.send_message(user_id, str(answer) + 'и что-то сломалось')

        if 'waterall-' in call.data:
            water = call.data.split('-')
            user_id = water[1]
            for plant_id in water[2:]:
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Растение полито")
                answer = water_plant(plant_id, user_id)
                if 'полито' in answer:
                    bot.send_message(user_id, str(answer))
                else:
                    bot.send_message(user_id, str(answer) + 'и что-то сломалось')
            bot.delete_message(user_id, call.message.message_id)
            memento(call.message)

        if 'fertile-' in call.data:
            fertile = call.data.split("-")
            plant_id = fertile[1]
            user_id = call.message.chat.id
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Растение удобрено")
            bot.delete_message(user_id, call.message.message_id)
            answer = fertile_plant(plant_id, user_id)
            if 'удобрено' in answer:
                bot.send_message(user_id, str(answer))
                plant_card(plant_id, user_id)
            else:
                bot.send_message(user_id, str(answer) + 'и что-то сломалось')

        if 'fertileall-' in call.data:
            fertile = call.data.split('-')
            user_id = fertile[1]
            for plant_id in fertile[2:]:
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Растение удобрено")
                answer = fertile_plant(plant_id, user_id)
                if 'удобрено' in answer:
                    bot.send_message(user_id, str(answer))
                else:
                    bot.send_message(user_id, str(answer) + 'и что-то сломалось')
            bot.delete_message(user_id, call.message.message_id)
            memento(call.message)

        if 'delete-' in call.data:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Dump the plant")

        if 'type-' in call.data:
            data = call.data.split('-')
            bot.send_message(call.message.chat.id,
                             f"Итак, имя: {data[1]}, вид: {data[2]}.\n\nОсталось вспомнить, когда растение последний "
                             f"раз поливали. Отправь дату в формате '01-01-2021'. Или отправь '1', чтобы я начал "
                             f"отсчет с сегодняшнего дня",
                             reply_markup=telebot.types.ForceReply())


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)

    except Exception as err:
        print('Something wrong! ', err)
