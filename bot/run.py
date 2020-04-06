import os
import json
import logging
import markovify

from functools import partial
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env
from mega import Mega

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


class ReplyBot:
    def __init__(self, filename, model_url):
        self.model = None
        try:
            if model_url:
                filename = Mega().download_url(
                    model_url,
                    os.path.dirname(filename))
            with open(filename, encoding='utf-8') as f:
                self.model = markovify.Text.from_json(json.load(f))
        except FileNotFoundError:
            logger.error(f"Model file {filename} is missing.")

    def reply(self):
        if self.model is None:
            return env("MESSAGE_DEFAULT")

        message = None
        while not message:
            message = self.model.make_sentence()
        return message


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
    message = model.reply()
    logger.info(f'Response to @{uname}: {message}')
    update.message.reply_text(message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


def main():
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - reply the message on Telegram
    bot = ReplyBot(MODEL_NAME, env.str("MODEL_URL", ""))
    dp.add_handler(MessageHandler(Filters.text, partial(reply, model=bot)))

    # log all errors
    dp.add_error_handler(error)

    # if not set, run in debug mode
    webhook_url = env.str("WEBHOOK_URL", "")

    if not webhook_url:
        updater.start_polling()
        updater.idle()
        return

    updater.start_webhook(
        listen="0.0.0.0",
        port=env.int("PORT", '8443'),
        url_path=TOKEN
    )
    updater.bot.set_webhook(f"{webhook_url}/{TOKEN}")
    updater.idle()


if __name__ == '__main__':
    main()
