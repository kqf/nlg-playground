import logging

from functools import partial
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from environs import Env
from bot.replybot import ReplyBot

env = Env()
env.read_env()

TOKEN = env("TOKEN")
MODEL_NAME = env("MODEL")
MESSAGE_START = env("MESSAGE_START")
MESSAGE_HELP = env("MESSAGE_HELP")
MESSAGE_VERSION = env("MESSAGE_VERSION")
MESSAGE_ABOUT = env("MESSAGE_ABOUT")

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


def version(update, context):
    update.message.reply_text(MESSAGE_VERSION)


def about(update, context):
    update.message.reply_text(MESSAGE_ABOUT)


def reply(update, context, model):
    """reply the user message."""
    uname = update.message.from_user.username
    logger.info(f'Message from @{uname}: {update.message.text}')
    message = model.reply(update, context)
    logger.info(f'Response to @{uname}: {message}')
    if message:
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
    dp.add_handler(CommandHandler("version", version))
    dp.add_handler(CommandHandler("about", about))

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
