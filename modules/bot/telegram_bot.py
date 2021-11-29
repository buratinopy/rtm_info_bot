import logging

import orjson
import telebot
from telebot import types

import environment as env
from modules import tofixed

from modules.bot import bot_tools

logger = logging.getLogger('rtm.bot')

if not env.bot:
    env.bot = telebot.TeleBot(env.settings['tg_token'])


@env.bot.message_handler(commands=['rtm'])
def rtm(message):
    """
    Отправка в чат сводной статистики по RTM
    :param message:
    :return:
    """
    bot_tools.rtm(message)


@env.bot.message_handler(commands=['help'])
def help(message):
    env.bot.reply_to(message, "Тут будет инструкция по работе с ботом... Soon..")


@env.bot.message_handler(commands=['how_to_help'])
def how_to_help(message):
    env.bot.reply_to(message, "You can support the project with donations "
                              "to the RTM address: RXzHTJBp313kV7GrDtUZy8gLNJQKGXupg2")


@env.bot.message_handler(commands=['nodes'])
def nodes(message):
    return_message = "<b>Какую информацию можно получить по нодам:</b>\n" \
                     "<b>/roi 10000</b> - расчёт доходности с ноды\n" \
                     "Другие опции в разработке...\n" \
                     "Свои идеи, пожелания, донаты можно слать ему @gagarin_first"
    env.bot.reply_to(message,
                     text=return_message,
                     parse_mode='html')


@env.bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
    """
    Инлайн подсчёт доходности по хешрейту
    :param inline_query:
    :return:
    """
    _title = None
    _result = None
    try:
        query = float(inline_query.query)
    except ValueError:
        _title = "Input you hashrate (H/s) [value must be type int or float]"
        query = 0
    try:
        if query > 0:
            _title = f"With hashrate {query}h/s you can get " \
                     f"~{tofixed(bot_tools.rtm_calculate_coins_per_day(query), 4)} RTM coins per day"

            _result = f"{_title}."
        r = types.InlineQueryResultArticle(id=1, title=_title,
                                           input_message_content=types.InputTextMessageContent(_result))
        env.bot.answer_inline_query(inline_query.id, [r])
    except Exception as exc:
        logger.error(exc)


@env.bot.message_handler(func=lambda message: True, content_types=['text'])
def chat(message):
    """ Работа с чатом """
    logger.debug("%s %s %s: %s", message.chat.id, message.from_user.first_name, message.from_user.last_name,
                 message.text)
    # node_roi
    if message.text.lower().startswith("/roi"):
        bot_tools.node_roi(message)
        return

    # convert
    if message.text.lower().startswith("/convert"):
        bot_tools.convert(message)
        return

    # dialog
    bot_tools.chat_dialog(message)


@env.bot.message_handler(content_types=["new_chat_members"])
def handler_new_member(message):
    """ Обработка события добавления пользователя в группу """
    bot_tools.new_member(message)
    return


def start_tg_bot():
    env.bot.infinity_polling()
