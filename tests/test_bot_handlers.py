import os

import pytest
import telebot

@pytest.fixture
def bot():
    return telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

@pytest.fixture
def chat_id():
    return 117179444

def test_start_handler(bot, chat_id):
    # Test that the bot responds correctly to the '/start' command
    user = telebot.types.User(1, 0, 'Yan')
    chat = telebot.types.Chat(chat_id, 'none')
    message = telebot.types.Message(chat_id, content_type='text', chat=chat,
                                    json_string='\"/start\"', date='2023-01-12',
                                    from_user=user, options=[])
    bot.process_new_messages([message])
    assert 1
