import telebot, configparser, os, json, requests
from telebot import types

server = '127.0.0.1:5000'

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


@bot.message_handler(commands=['list'])
def get_plant_list(message):
    print(message)

@bot.message_handler()
def check_update(message):
    bot.send_message(message.chat.id, message.from_user)




# @bot.message_handler(content_types=["text"])
# def repeat_all_messages(message): # Название функции не играет никакой роли
#     bot.send_message(message.chat.id, message.text)
#     print(message)



if __name__ == '__main__':
     bot.polling(none_stop=True)

