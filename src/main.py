"""Телеграм бот, который ..."""
import os
import sys
import logging
import telebot
from db.bot_db import UserGroupDB, DBStatus
from api.solver import Person, Solver

token = os.environ['TELEGRAM_BOT_TOKEN']
bot = telebot.TeleBot(token)

FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)

# auxiliary tools
table: UserGroupDB = None
solver: Solver = Solver()


@bot.message_handler(commands=['start'], content_types=['text'])
def start_handler(message):
    text = 'Привет!'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['help'], content_types=['text'])
def help_handler(message):
    text = 'Привет! Список допустимых команд: \n' \
           '/help - короткая информация о возможностях бота\n' \
           '/create_group groupName - создать группу с названием groupName и возвращает groupId, ' \
           'по которому в дальнейшем можно делать операции с ней\n' \
           '/add_user groupId groupName userName City\n добавить участника в группу groupId, с именем userName, ' \
           'который будет лететь из города City\n' \
           '/delete_user groupId groupName userName City - удалить пользователя с именем userName из группы groupId\n' \
           '/view_group groupId groupName - посмотреть список всех участников группы groupId\n' \
           '/find_flights groupId groupName date - найти город, в который дешевле всего будет попасть группе groupId.\n' \
           'Формат даты: YYYY-MM-DD'
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
    group_id, status = table.add_group(group_name)
    logger.info(f'Process of creating group with name {group_name} finished with status: {status}')
    if status == DBStatus.SUCCESS:
        text = f'Созданна группа с названием {group_name}\n' \
               f'groupId - {group_id}'
    else:
        text = 'Возникли проблемы!'

    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['add_user'], content_types=['text'])
def add_user_handler(message):
    args = message.text.split()
    if len(args) < 5:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для добавления пользователя. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    group_name = args[2]
    user_name = args[3]
    city = args[4]

    status = table.add_user(group_id, group_name, user_name, city)
    logger.info(f'add user {user_name} status: {status}')
    if status == DBStatus.SUCCESS:
        text = f'Добавлен пользователь в группу с id {group_id}'
    else:
        text = 'Возникли проблемы!'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['delete_user'], content_types=['text'])
def delete_user_handler(message):
    args = message.text.split()
    if len(args) < 4:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для удаления пользователя. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    group_name = args[2]
    user_name = args[3]

    status = table.delete_user(group_id, group_name, user_name)
    logger.info(f'delete user {user_name} status: {status}')
    if status == DBStatus.SUCCESS:
        text = f'Удален пользователь из группы с id {group_id}'
    else:
        text = 'Возникли проблемы!'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['view_group'], content_types=['text'])
def view_group_handler(message):
    args = message.text.split()
    if len(args) < 3:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для просмотра группы. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    group_name = args[2]

    group_list = table.view_group(group_id, group_name)
    logger.info(f'View group {group_name} info: {group_list}')
    text = f'Список участников группы с id {group_id}:\n'
    if group_list is not None:
        for user in group_list:
            text += f'[name={user[0]}, city={user[1]}]\n'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['find_flights'], content_types=['text'])
def find_flights_handler(message):
    args = message.text.split()
    if len(args) < 4:
        logger.warning('Too few arguments')
        text = 'Недостаточно аргументов для просмотра группы. Попробуйте еще раз!'
        bot.send_message(message.from_user.id, text)
        return
    group_id = args[1]
    group_name = args[2]
    date = args[3]

    group_list = table.view_group(group_id, group_name)
    people = []
    for user in group_list:
        people.append(Person(user[1]))
    info = solver.get_cheapest_meeting(people, date)
    if info is not None:
        text = f'Flight info:\n' \
               f'City: {info[1]}\n' \
               f'Price: {info[0]}'
    else:
        text = 'Нет информации'
    logger.info(f'Flight info: {info}')
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
    table = UserGroupDB(db_path)
    if len(sys.argv) == 1 or sys.argv[1] == '1':
        logger.info(f'create_table status: {table.recreate_table()}')
    bot.polling(none_stop=True, interval=0)
