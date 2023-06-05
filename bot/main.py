import logging
from functools import partial

from telegram.ext import Application, CommandHandler, MessageHandler, filters

import bot.settings as config
from bot.replybot import ReplyBot

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def start(update, context):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(config.message_start)


async def help(update, context):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(config.message_help)


async def version(update, context):
    await update.message.reply_text(config.message_version)


async def about(update, context):
    await update.message.reply_text(config.message_about)


async def reply(update, context, model):
    """reply the user message."""
    uname = update.message.from_user.username
    message = model.reply(update, context)

    await context.bot.send_message(
        chat_id=config.admin_id,
        text=f"@{uname}:\n{update.message.text}\n\n🤖:\n{message}",
    )
    logger.info(f"Message from @{uname}: {update.message.text}")
    logger.info(f"Response to @{uname}: {message}")
    if message:
        await update.message.reply_text(message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    app = Application.builder().token(config.token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("version", version))
    app.add_handler(CommandHandler("about", about))

    # on noncommand i.e message - reply the message on Telegram
    bot = ReplyBot(config.model_name, config.model_url)
    app.add_handler(MessageHandler(filters.TEXT, partial(reply, model=bot)))
    # log all errors
    app.add_error_handler(error)
    if not config.webhook:
        app.run_polling()
        return

    app.run_webhook(
        listen="0.0.0.0",
        port=config.port,
        url_path=config.token,
        webhook_url=config.webhook,
    )


if __name__ == "__main__":
    main()
