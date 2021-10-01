# import aiogram, os, configparser
#
# path = os.path.dirname(__file__)
# configfile = os.path.join(path, 'settings.ini')
# config = configparser.ConfigParser()
# config.read(configfile)
# token = config['telegram']['bot-api']
#
# tgbot = aiogram.Bot(token=token)
# bot = aiogram.Dispatcher(tgbot)
#
# @bot.message_handler(commands='/start')
# def start_talking(msg):
#     bot.send_message()
#
#
# @bot.message_handler(content_types=['text'])
# def all_messages(message):
#     user_id = message.from_user.id
#     msg_id = message.message_id
#     body = 'message {msg_id} = {message}\n' \
#            '--\n' \
#            'first - {first}, last - {last}\n' \
#            'name {username}, id - {id}'.format(msg_id=msg_id, message=message.text, first=message.from_user.first_name,
#                                                last=message.from_user.last_name, username=message.from_user.username,
#                                                id=message.from_user.id)
#     bot.send_message(user_id, body)
#
#
# # if __name__ == '__main__':
# #     bot.polling(none_stop=True)
#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
import asyncio
import aiogram
import aiohttp
import logging
import os, configparser

path = os.path.dirname(__file__)
configfile = os.path.join(path, 'settings.ini')
config = configparser.ConfigParser()
config.read(configfile)
token = config['telegram']['bot-api']

tgbot = aiogram.Bot(token=token)
dp = aiogram.Dispatcher(tgbot)

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Хэндлер на команду /test1
@dp.message_handler(commands="test1")
async def cmd_test1(message: aiogram.types.Message):
    await message.reply("Test 1")

# Хэндлер на команду /test2
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")

# Где-то в другом месте...
dp.register_message_handler(cmd_test2, commands="test2")


if __name__ == "__main__":
    # Запуск бота
    aiogram.executor.start_polling(dp, skip_updates=True)
