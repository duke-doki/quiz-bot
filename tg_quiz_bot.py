import argparse
import logging

import redis
from environs import Env
from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

from questions_handler import get_question, get_quiz_pairs
from vk_quiz_bot import error_handler

logger = logging.getLogger(__name__)
QUESTION, ANSWER, GIVE_UP = range(3)


def start(update, context):
    update.message.reply_markdown_v2(
        r'Здравствуйте\!',
        reply_markup=ReplyKeyboardMarkup(
            [
                ['Новый вопрос', ],
            ]
        )
    )
    return QUESTION


def handle_new_question_request(update, context, database):
    user_id = update.effective_user.id
    question = get_question(quiz)
    database.set(user_id, question)
    update.message.reply_text(
        question,
        reply_markup=ReplyKeyboardMarkup(
            [
                ['Новый вопрос', 'Сдаться'],
                ['Мой счет']
            ]
        )
    )
    return ANSWER


def handle_solution_attempt(update, context, database):
    user_id = update.effective_user.id
    if database.get(user_id):
        stored_question = database.get(user_id)
        decoded_question = stored_question.decode('utf-8')
        answer = update.message.text
        correct_answer = quiz[decoded_question]
        if '(' in correct_answer:
            correct_answer_parts = correct_answer.split('(')
        else:
            correct_answer_parts = correct_answer.split('.')
        correct_answer_prefix = correct_answer_parts[0].strip()
        if answer == 'Новый вопрос':
            return handle_new_question_request(update, context, database)
        if answer == 'Сдаться':
            return concede_defeat(update, context, database)
        elif correct_answer_prefix in answer:
            update.message.reply_text(
                "Правильно! Поздравляю! "
                "Для следующего вопроса нажми 'Новый вопрос'",
                reply_markup=ReplyKeyboardMarkup(
                    [
                        ['Новый вопрос', 'Сдаться'],
                        ['Мой счет']
                    ]
                )
            )
        else:
            update.message.reply_text(
                "Неправильно... Попробуешь ещё раз?",
                reply_markup=ReplyKeyboardMarkup(
                    [
                        ['Новый вопрос', 'Сдаться'],
                        ['Мой счет']
                    ]
                )
            )
            return ANSWER


def concede_defeat(update, context, database):
    user_id = update.effective_user.id
    stored_question = database.get(user_id)
    decoded_question = stored_question.decode('utf-8')
    correct_answer = quiz[decoded_question]
    context.bot.send_message(
        chat_id=user_id,
        text=f'Правильный ответ: {correct_answer}\nСледующий вопрос:'
    )
    return handle_new_question_request(update, context, database)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    env = Env()
    env.read_env()
    tg_token = env.str('TG_TOKEN')
    master_id = env.str('MASTER_ID')
    parser = argparse.ArgumentParser(
        description='This script allows to run a quiz via tg bot'
    )
    parser.add_argument(
        'txt_file',
        help="enter the txt file name"
    )
    args = parser.parse_args()
    txt_file = args.txt_file
    quiz = get_quiz_pairs(txt_file)
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        updater = Updater(tg_token)

        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={
                QUESTION: [
                    MessageHandler(
                        Filters.regex(r'^Новый вопрос$'),
                        lambda update, context: handle_new_question_request(
                            update,
                            context,
                            r
                        )
                    )
                ],
                ANSWER: [
                    MessageHandler(
                        Filters.text,
                        lambda update, context: handle_solution_attempt(
                            update,
                            context,
                            r
                        )
                    )
                ],
                GIVE_UP: [
                    MessageHandler(
                        Filters.regex(r'^Сдаться$'),
                        lambda update, context: concede_defeat(
                            update,
                            context,
                            r
                        )
                    )
                ],
            },
            fallbacks=[]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()

        updater.idle()
    except Exception as e:
        error_handler(e, tg_token, master_id)
