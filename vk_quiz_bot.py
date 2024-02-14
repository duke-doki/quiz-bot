import argparse
import random

import redis
import telegram
import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

from questions_handler import get_quiz_pairs, get_question


def handle_new_question_request(event, vk_api, keyboard):
    user_id = event.user_id
    question = get_question(quiz)
    r.set(user_id, question)
    stored_question = r.get(user_id)
    decoded_question = stored_question.decode('utf-8')
    vk_api.messages.send(
        user_id=user_id,
        message=decoded_question,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_solution_attempt(event, vk_api, keyboard):
    user_id = event.user_id
    if r.get(user_id):
        stored_question = r.get(user_id)
        decoded_question = stored_question.decode('utf-8')
        answer = event.text
        correct_answer = quiz[decoded_question]
        if '(' in correct_answer:
            correct_answer_parts = correct_answer.split('(')
        else:
            correct_answer_parts = correct_answer.split('.')
        correct_answer_prefix = correct_answer_parts[0].strip()
        if answer == 'Новый вопрос':
            return handle_new_question_request(event, vk_api, keyboard)
        if answer == 'Сдаться':
            return concede_defeat(event, vk_api, keyboard)
        elif correct_answer_prefix in answer:
            vk_api.messages.send(
                user_id=user_id,
                message="Правильно! Поздравляю! Для следующего вопроса нажми "
                        "'Новый вопрос'",
                random_id=random.randint(1, 1000),
                keyboard=keyboard.get_keyboard(),
            )
        else:
            vk_api.messages.send(
                user_id=user_id,
                message="Неправильно... Попробуешь ещё раз?",
                random_id=random.randint(1, 1000),
                keyboard=keyboard.get_keyboard(),
            )
    else:
        vk_api.messages.send(
            user_id=user_id,
            message="Не понял команду. Попробуйте еще раз.",
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard(),
        )


def concede_defeat(event, vk_api, keyboard):
    user_id = event.user_id
    stored_question = r.get(user_id)
    decoded_question = stored_question.decode('utf-8')
    correct_answer = quiz[decoded_question]
    vk_api.messages.send(
        user_id=user_id,
        message=f"Правильный ответ: {correct_answer}\nСледующий вопрос:",
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )
    return handle_new_question_request(event, vk_api, keyboard)


def error_handler(text, tg_token, master_id):
    bot = telegram.Bot(token=tg_token)
    bot.send_message(text=text, chat_id=master_id)


if __name__ == "__main__":
    env = Env()
    env.read_env()
    vk_token = env.str('VK_TOKEN')
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
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Новый вопрос')
        keyboard.add_button('Сдаться')
        keyboard.add_line()
        keyboard.add_button('Мой счёт')
        vk_session = vk.VkApi(token=vk_token)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == "Новый вопрос":
                    handle_new_question_request(event, vk_api, keyboard)
                if event.text == "Сдаться":
                    concede_defeat(event, vk_api, keyboard)
                if event.text == "Мой счёт":
                    pass
                elif event.text not in ["Новый вопрос", "Сдаться", "Мой счёт"]:
                    handle_solution_attempt(event, vk_api, keyboard)
    except Exception as e:
        error_handler(e, tg_token, master_id)
