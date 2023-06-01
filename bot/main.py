import logging
from functools import partial

from environs import Env
from telegram.ext import Application, MessageHandler, filters

# import os


# from bot.replybot import ReplyBot

env = Env()
env.read_env()

TOKEN = env("TOKEN")
MODEL_NAME = env("MODEL")
MESSAGE_START = env("MESSAGE_START")
MESSAGE_HELP = env("MESSAGE_HELP")
MESSAGE_VERSION = env("MESSAGE_VERSION")
MESSAGE_ABOUT = env("MESSAGE_ABOUT")
WEBHOOK_URL = env.str("WEBHOOK_URL", "")
PORT = env.str("PORT", "")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start(update, context):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(MESSAGE_START)


async def help(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(MESSAGE_HELP)


async def version(update, context):
    await update.message.reply_text(MESSAGE_VERSION)


async def about(update, context):
    await update.message.reply_text(MESSAGE_ABOUT)


async def reply(update, context, model):
    """reply the user message."""
    uname = update.message.from_user.username
    logger.info(f"Message from @{uname}: {update.message.text}")
    # message = model.reply(update, context)
    message = "test message"
    logger.info(f"Response to @{uname}: {message}")
    if message:
        await update.message.reply_text(message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    app = Application.builder().token(TOKEN).build()
    # app.add_handler(CommandHandler("start", start))
    # app.add_handler(CommandHandler("help", help))
    # app.add_handler(CommandHandler("version", version))
    # app.add_handler(CommandHandler("about", about))

    # # on noncommand i.e message - reply the message on Telegram
    # # bot = ReplyBot(MODEL_NAME, env.str("MODEL_URL", ""))
    # logger.info("Downloaded")
    # logger.info("The folders are here")
    # logger.info(os.listdir())
    app.add_handler(MessageHandler(filters.TEXT, partial(reply, model="1234")))
    # log all errors
    # app.add_error_handler(error)
    if not WEBHOOK_URL:
        app.run_polling()
        return

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    main()
