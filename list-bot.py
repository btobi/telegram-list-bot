# coding=utf-8
import atexit
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])
dispatcher = updater.dispatcher

userids = [int(userid) for userid in os.environ['TELEGRAM_BOT_USERS'].split(" ")]

list_items = []


def send_message(message):
    for userid in userids:
        try:
            updater.bot.send_message(chat_id=userid, text=message, parse_mode=ParseMode.HTML)
        except BadRequest:
            print("Error sending message ... \" \n {} \n \" to user {}.".format(message, userid))


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        bot.send_message(chat_id=update.message.chat_id, text="Unauthorized")
    except BadRequest:
        bot.send_message(chat_id=update.message.chat_id, text="Bad request")
    except TimedOut:
        bot.send_message(chat_id=update.message.chat_id, text="Timeout")
    except NetworkError:
        bot.send_message(chat_id=update.message.chat_id, text="Network error")
    except ChatMigrated as e:
        bot.send_message(chat_id=update.message.chat_id, text="Chat has migrated")
    except TelegramError:
        bot.send_message(chat_id=update.message.chat_id, text="Telegram Error")


def add_item(bot, update):
    if update.message.from_user.id not in userids:
        update.message.reply_text('Unerlaubter Zugriff')
        return
    list_items.append(update.message.text)
    print_items(new_item=update.message.text)


def print_items(update=None, new_item=None, deleted_item=None):
    message = ""

    if new_item:
        message = "{} wurde zur Einkaufsliste hinzugefügt. \n".format(new_item)
    if deleted_item:
        message = "{} wurde von der Einkaufsliste gelöscht. \n".format(deleted_item)

    message += "\n"

    message += "Vollständige Liste: \n"

    if len(list_items) == 0:
        message += "Leer"

    message += "\n".join(list_items)
    if update:
        update.message.reply_text(message)
    else:
        send_message(message)


def delete_item(bot, update, args):
    list_items.remove(args[0])
    print_items(deleted_item=args[0])


def only_list(bot, update):
    print_items(update)


def clear_list(bot, update):
    global list_items
    list_items = []
    send_message("Liste gelöscht")


def help_message(bot, update):
    message = "*Folgende Befehle sind möglich:* \n"
    commands = [
        "Element - Element hinzufügen",
        "/list - Liste anzeigen",
        "/clear - Liste leeren",
        "/del Element - Element löschen",
        "/help - Diese Hilfe anzeigen",
    ]
    message += "\n".join(commands)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


def welcome(bot, update):
    update.message.reply_text("Willkommen bei der Einkaufsliste!")
    help_message(bot, update)


def run_bot():
    dispatcher.add_handler(CommandHandler("del", delete_item, pass_args=True))
    dispatcher.add_handler(CommandHandler("list", only_list))
    dispatcher.add_handler(CommandHandler("clear", clear_list))
    dispatcher.add_handler(CommandHandler("help", help_message))
    dispatcher.add_handler(CommandHandler("start", welcome))
    dispatcher.add_handler(MessageHandler(Filters.text, add_item))
    dispatcher.add_error_handler(error_callback)

    send_message("/start")

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()
