import json
import logging
import markovify

from functools import partial
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env

env = Env()
env.read_env()

TOKEN = env("TOKEN")
MODEL_NAME = env("MODEL")
MESSAGE_START = env("MESSAGE_START")
MESSAGE_HELP = env("MESSAGE_HELP")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(MESSAGE_START)


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text(MESSAGE_HELP)


def reply(update, context, model):
    """reply the user message."""
    uname = update.message.from_user.username
    logger.info(f'Message from @{uname}: {update.message.text}')
    message = ""
    while not message:
        message = model.make_sentence()
    logger.info(f'Response to @{uname}: {message}')
    update.message.reply_text(message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    with open(MODEL_NAME, encoding='utf-8') as f:
        model = markovify.Text.from_json(json.load(f))

    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - reply the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, partial(reply, model=model)))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
