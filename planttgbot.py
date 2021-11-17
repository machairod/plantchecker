import telebot, configparser, os, json, requests
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
    fertile_btn = types.InlineKeyboardButton('Удобрить', callback_data="fertile-"+str(plant_id))
    delete_btn = types.InlineKeyboardButton('Удалить растение', callback_data="delete-"+str(plant_id))
    card_markup.add(water_btn, fertile_btn)
    card_markup.add(list_btn)
    card_markup.add(delete_btn)

    # запрос данных растения из базы
    # plant_url = server + f"plants/{plant_id}?login={user_id}"  --------- не забыть переставить на айди пользователя!!!!
    plant_url = server + f"plants/{plant_id}?login=linlynx"
    response = requests.get(plant_url)
    plantcard = json.loads(response.json())

    msg = f"{plantcard['plantname']}, вид: {plantcard['plantspec']}\n\n" \
          f"Следующая дата полива: {plantcard['next_water']}\n" \
          f"Следующая дата удобрения: {plantcard['next_fertile']}\n" \
          f"Яркость освещения: {plantcard['light']} из 3.\n" \
          f"Опрыскивание: "+("рекомендуется" if plantcard["spraying"] == 1 else "не рекомендуется")

    bot.send_message(user_id, msg, reply_markup=card_markup)

def water_plant(plant_id,user_id, **kwargs):
    name
    plantname
    login


@bot.message_handler(commands=['start'])
def start_message(message):
    name = message.from_user.first_name if message.from_user.first_name is not None else "@"+message.from_user.username
    bot.send_message(message.chat.id,f'Привет, {name}, я бот для своевременного ухода за растениями.')

@bot.message_handler(commands=['plantlist'])
def get_plant_list(message):
    # plant_url = server + f"plants/?login={message.from_user.id}" - не забыть активировать для актуального пользователя!!!!
    plant_url = server + f"plants/?login=linlynx"
    response = requests.get(plant_url)

    plantlist = json.loads(response.json())

    list_markup = types.InlineKeyboardMarkup()
    for i in plantlist:
        btn = types.InlineKeyboardButton(i, callback_data="card-"+str(plantlist[i]['id']))
        list_markup.add(btn)

    bot.send_message(message.chat.id, f'В вашем списке - {len(plantlist)} растений :', disable_notification=True,
                         reply_markup=list_markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
     if call.message:
        if "card" in call.data:
            plant_id = call.data.lstrip("card-")
            user_id = call.message.chat.id
            bot.delete_message(call.message.chat.id, call.message.message_id)
            plant_card(plant_id, user_id)

        if 'list' in call.data:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            get_plant_list(call.message)

        if 'water' in call.data:
            water = call.data.split("-")
            plant_id = water[1]
            user_id = call.message.chat.id
            water_plant(plant_id,user_id)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Water for plant")

        if 'fertile' in call.data:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Fertile the plant")

        if 'delete' in call.data:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Dump the plant")


     # if call.message:
     #    if call.data == "amir":
     #        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="TweenRoBOT Created By @This_Is_Amir And Written In Python")
     # if call.message:
     #    if call.data == "sticker":
     #        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=":D")
     #        r = redis.hget('file_id',call.message.chat.id)
     #        bot.send_sticker(call.message.chat.id, '{}'.format(r))
     # if call.message:
     #    if call.data == "document":
     #        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=":D")
     #        r = redis.hget('file_id',call.message.chat.id)
     #        bot.send_document(call.message.chat.id, '{}'.format(r))


# @bot.message_handler(content_types=["text"])
# def default_test(message):
#     keyboard = types.InlineKeyboardMarkup()
#     url_button = types.InlineKeyboardButton(text="Перейти на Яндекс", url="https://ya.ru")
#     keyboard.add(url_button)
#     bot.send_message(message.chat.id, "Привет! Нажми на кнопку и перейди в поисковик.", reply_markup=keyboard)

if __name__ == '__main__':
    bot.polling(none_stop=True)

