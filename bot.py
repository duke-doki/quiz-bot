import logging
from environs import Env
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    Filters
)
import redis
from functions import send_question

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте',
        reply_markup=ForceReply(selective=True),
    )


def message(update: Update, context: CallbackContext) -> None:
    if update.message.text == 'Новый вопрос':
        update.message.reply_text(
            send_question(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    ['Новый вопрос', 'Сдаться'],
                    ['Мой счет']
                ]
            )
        )
    else:
        update.message.reply_text(
            update.message.text,
            reply_markup=ReplyKeyboardMarkup(
                [
                    ['Новый вопрос', 'Сдаться'],
                    ['Мой счет']
                ]
            )
        )


def main() -> None:
    env = Env()
    env.read_env()
    host = env.str('HOST')
    port = env.int('PORT')
    password = env.str('PASSWORD')
    r = redis.Redis(host=host, port=port, password=password)
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"Retrieved value for 'test_key': {value.decode('utf-8')}")
    r.close()
    tg_token = env.str('TG_TOKEN')
    updater = Updater(tg_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command, message
        )
    )

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
