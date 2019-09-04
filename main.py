import os
import logging
import telegram
from train_dialogflow_api import train_bot, get_dialog_response
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "verbsgameagent-dsmofb-090249edded3.json"


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(text="Здравствуйте")


def echo(bot, update):
    """Echo the user message."""
    session_id = update.message.chat_id
    text = get_dialog_response(session_id, update.message.text)['response_text']
    update.message.reply_text(text)


def train(bot, update):
    """Echo the user message."""
    train_bot("questions.json", True)
    update.message.reply_text(text="Тренировка DialoglowAPI")


def main():
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    user_chat_id = os.getenv("USER_CHAT_ID")

    """Start the bot."""
    updater = Updater(telegram_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("train", train))
    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()


if __name__ == '__main__':
    main()
