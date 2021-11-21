import configparser
import json
import os
import requests
import telebot
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

    water_url = server + '/plants/water/'
    jdata = {'id': plant_id, 'login': login, 'name': plantname, 'user_id': user_id, 'date': date}
    jdata = json.dumps(jdata, ensure_ascii=False)

    response = requests.put(water_url, json=jdata)
    if 'полито' in response.text:
        bot.send_message(login, str(response.text))
        plant_card(plant_id, login)
    else:
        bot.send_message(login, str(response.text) + 'и что-то сломалось')


def fertile_plant(plant_id, login, **kwargs):
    date = None
    plantname = None
    user_id = None
    if len(kwargs) > 0:
        plantname = kwargs.get('plantname')
        user_id = kwargs.get('user_id')

    fertile_url = server + '/plants/fertile/'
    jdata = {'id': plant_id, 'login': login, 'name': plantname, 'user_id': user_id, 'date': date}
    jdata = json.dumps(jdata, ensure_ascii=False)

    response = requests.put(fertile_url, json=jdata)
    if 'удобрено' in response.text:
        bot.send_message(login, str(response.text))
        plant_card(plant_id, login)
    else:
        bot.send_message(login, str(response.text) + 'и что-то сломалось')


@bot.message_handler(commands=['start'])
def start_message(message):
    name = message.from_user.first_name if message.from_user.first_name is not None else "@" + message.from_user.username
    bot.send_message(message.chat.id, f'Привет, {name}, я бот для своевременного ухода за растениями.')


@bot.message_handler(commands=['plantlist'])
def get_plant_list(message):
    plant_url = server + f"plants/?login={message.from_user.id}"
    response = requests.get(plant_url)
    user_id = message.chat.id

    plantlist = json.loads(response.json())

    list_markup = types.InlineKeyboardMarkup()
    for i in plantlist:
        btn = types.InlineKeyboardButton(i, callback_data="card-" + str(plantlist[i]['id']) + "-" + str(user_id))
        list_markup.add(btn)

    bot.send_message(user_id, f'В вашем списке - {len(plantlist)} растений :', disable_notification=True,
                     reply_markup=list_markup)


@bot.message_handler(commands=['memento'])
def memento(message):
    user_id = message.chat.id
    memento_url = server + f'memento/?login={user_id}'
    response = requests.get(memento_url)

    memento_list = json.loads(response.json())
    bot.send_message(user_id, memento_list[0])


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if "card" in call.data:
            carddata = call.data.split('-')
            user_id = carddata[2]
            plant_id = carddata[1]
            bot.delete_message(call.message.chat.id, call.message.message_id)
            plant_card(plant_id, user_id)

        if 'list' in call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            get_plant_list(call.message)

        if 'water' in call.data:
            water = call.data.split("-")
            plant_id = water[1]
            user_id = call.message.chat.id
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Растение полито")
            bot.delete_message(user_id, call.message.message_id)
            water_plant(plant_id, user_id)

        if 'fertile' in call.data:
            fertile = call.data.split("-")
            plant_id = fertile[1]
            user_id = call.message.chat.id
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Растение полито")
            bot.delete_message(user_id, call.message.message_id)
            fertile_plant(plant_id, user_id)

        if 'delete' in call.data:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Dump the plant")


if __name__ == '__main__':
    bot.polling(none_stop=True)
