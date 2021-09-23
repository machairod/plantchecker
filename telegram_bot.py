import telebot, os, configparser

path = os.path.dirname(__file__)
configfile = os.path.join(path, 'settings.ini')
config = configparser.ConfigParser()
config.read(configfile)
token = config['telegram']['bot-api']

bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['text'])
def all_messages(msg):
    message = msg.text
    user_id = msg.from_user.id
    bot.send_message(user_id, f"Вы написали: {message}")


if __name__ == '__main__':
    bot.polling(none_stop=True)