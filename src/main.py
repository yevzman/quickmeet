"""Телеграм бот, который ..."""
import os
import logging
import telebot
from db.bot_db import create_table, BotDB

token = os.environ['TELEGRAM_BOT_TOKEN']
bot = telebot.TeleBot(token)

FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start'], content_types=['text'])
def start_handler(message):
    text = 'Привет!'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['help'], content_types=['text'])
def help_handler(message):
    text = 'Привет! Список допустимых команд: \n' \
           '/help - короткая информация о возможностях бота\n' \
           '/create_group groupName - создать группу с названием groupName и возвращает groupId, ' \
                                           'по которому в дальнейшем можно делать преобразования с ней\n' \
           '/add_user groupId userName City\n добавить участника в группу groupId, с именем userName, ' \
                                                                'который будет лететь из города City\n' \
           '/delete_user groupId userName City - удалить пользователя с именем userName из группы groupId\n' \
           '/view_group groupId - посмотреть список всех участников группы groupId\n' \
           '/find_flights groupId variantsAmount - найти город, в который дешевле всего будет попасть группе groupId'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['create_group'], content_types=['text'])
def create_group_handler(message):
    args = message.text.split()
    if len(args) < 2:
        logger.warning('Too few arguments')
        text = 'Вы забыли ввести название группы. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_name = args[1]
    group_id = table.add_group(group_name)

    text = f'Созданна группа с названием {group_name}\n' \
           f'groupId - {group_id}'

    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['add_user'], content_types=['text'])
def add_user_handler(message):
    args = message.text.split()
    if len(args) < 4:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для добавления пользователя. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    user_name = args[2]
    city = args[3]
    # table.add_user(group_id, group_name, user_name, city)
    text = f'Добавлен пользователь в группу с id {group_id}'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['delete_user'], content_types=['text'])
def delete_user_handler(message):
    args = message.text.split()
    if len(args) < 3:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для удаления пользователя. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    user_name = args[2]
    # table.delete_user(group_id, 'group_name?')
    text = f'Удален пользователь из группы с id {group_id}'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['view_group'], content_types=['text'])
def view_group_handler(message):
    args = message.text.split()
    if len(args) < 2:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для просмотра группы. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    # print('View', table.view_group(group_id, group_name))
    text = f'Список участников группы с id {group_id}:'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['find_flights'], content_types=['text'])
def find_flights_handler(message):
    args = message.text.split()
    if len(args) < 2:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для просмотра группы. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    flights_amount = 1 if len(args) < 3 else int(args[2])
    text = 'Пока что не умею искать билеты...'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(content_types=['text'])
def other_text_handler(message):
    text = 'Я не понимаю команду.....!\n'
    bot.send_message(message.from_user.id, text)


if __name__ == '__main__':
    """Начало работы бота"""
    logger.setLevel(level='INFO')
    logger.info('Starting bot')
    db_path = 'db/data.db'  # Позже будет доставаться из окружения
    logger.info('create_table status: ' + str(create_table(db_path)))
    table = BotDB(db_path)
    bot.polling(none_stop=True, interval=0)
