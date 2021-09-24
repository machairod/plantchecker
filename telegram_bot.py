import aiogram, os, configparser

path = os.path.dirname(__file__)
configfile = os.path.join(path, 'settings.ini')
config = configparser.ConfigParser()
config.read(configfile)
token = config['telegram']['bot-api']

tgbot = aiogram.Bot(token=token)
bot = aiogram.Dispatcher(tgbot)

@bot.message_handler(commands='/start')
def start_talking(msg):
    bot.send_message()


@bot.message_handler(content_types=['text'])
def all_messages(message):
    user_id = message.from_user.id
    msg_id = message.message_id
    body = 'message {msg_id} = {message}\n' \
           '--\n' \
           'first - {first}, last - {last}\n' \
           'name {username}, id - {id}'.format(msg_id=msg_id, message=message.text, first=message.from_user.first_name,
                                               last=message.from_user.last_name, username=message.from_user.username,
                                               id=message.from_user.id)
    bot.send_message(user_id, body)


# if __name__ == '__main__':
#     bot.polling(none_stop=True)
