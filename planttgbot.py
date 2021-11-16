import telebot, configparser, os, json, requests
from telebot import types

server = 'http://127.0.0.1:5000/'

path = os.path.dirname(__file__)
config = configparser.ConfigParser()

configfile = os.path.join(path, 'settings.ini')
config.read(configfile)

token = config['telegram']['bot-token']
bot = telebot.TeleBot(token)



@bot.message_handler(commands=['start'])
def start_message(message):
    name = message.from_user.first_name if message.from_user.first_name is not None else "@"+message.from_user.username
    bot.send_message(message.chat.id,f'Привет, {name}, я бот для своевременного ухода за растениями.')

@bot.message_handler(commands=['plantlist'])
def get_plant_list(message):
    plant_url = server + f"plants/?login={message.from_user.id}"
    plant_url = server + f"plants/?login=linlynx"
    response = requests.get(plant_url)
    plantlist = json.loads(response.json())

    markup = types.InlineKeyboardMarkup()
    for i in plantlist:

    b = types.InlineKeyboardButton("Help", callback_data='help')
    c = types.InlineKeyboardButton("About", callback_data='amir')
    markup.add(b, c)
    nn = types.InlineKeyboardButton("Inline Mode", switch_inline_query='')
    oo = types.InlineKeyboardButton("Channel", url='https://telegram.me/offlineteam')
    markup.add(nn, oo)
    bot.send_message(message.chat.id, f'В вашем списке - {len(plantlist)} растений :', disable_notification=True,
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
     if call.message:
        if call.data == "help":
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Помогай себе сам")
     if call.message:
        if call.data == "amir":
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="TweenRoBOT Created By @This_Is_Amir And Written In Python")
     if call.message:
        if call.data == "sticker":
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=":D")
            r = redis.hget('file_id',call.message.chat.id)
            bot.send_sticker(call.message.chat.id, '{}'.format(r))
     if call.message:
        if call.data == "document":
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=":D")
            r = redis.hget('file_id',call.message.chat.id)
            bot.send_document(call.message.chat.id, '{}'.format(r))


# @bot.message_handler(content_types=["text"])
# def default_test(message):
#     keyboard = types.InlineKeyboardMarkup()
#     url_button = types.InlineKeyboardButton(text="Перейти на Яндекс", url="https://ya.ru")
#     keyboard.add(url_button)
#     bot.send_message(message.chat.id, "Привет! Нажми на кнопку и перейди в поисковик.", reply_markup=keyboard)




# @bot.message_handler(content_types=["text"])
# def repeat_all_messages(message): # Название функции не играет никакой роли
#     bot.send_message(message.chat.id, message.text)
#     print(message)


if __name__ == '__main__':
     bot.polling(none_stop=True)
