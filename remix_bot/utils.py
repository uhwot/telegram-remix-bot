import pymongo
import re

from telegram import Update
from telegram.ext import BaseFilter, CallbackContext
from telegram.error import BadRequest

from . import DB_URL, GROUP_ID, OWNER_ID
from .mwt import MWT

db_client = pymongo.MongoClient(DB_URL)
whitelist_db = db_client["whitelist"]

global_db = db_client["global"]
userlog = global_db["users"]


@MWT(timeout=3600)
def get_admin_ids(bot, chat_id):
    # Returns a list of admin IDs for a given chat. Results are cached for 1 hour.
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def delete(message):
    # Prevents exception if message is already deleted.
    try:
        message.delete()
    except BadRequest:
        pass


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def get_id(username):
    try:
        return userlog.find_one({"username": re.compile(username, re.IGNORECASE)}, {"id": 1})["id"]
    except TypeError:
        raise KeyError


def get_name(username):
    try:
        return userlog.find_one({"username": re.compile(username, re.IGNORECASE)}, {"name": 1})["name"]
    except TypeError:
        raise KeyError


def insert_user(id, username, name):
    temp = {"id": id, "username": username, "name": name}
    return userlog.replace_one({"id": id}, temp, upsert=True)


def whitelisted(user_id, chat_id):
    if not DB_URL:
        return False

    whitelist = whitelist_db[str(chat_id)]
    if whitelist.find_one({"id": user_id}):
        return True
    else:
        return False

# Decorators

def group_id(func):
    def wrapper(update: Update, *args, **kwargs):
        if not GROUP_ID:
            func(update, *args, **kwargs)

        if str(update.effective_chat.id) in GROUP_ID:
            func(update, *args, **kwargs)
    return wrapper


def username(func):
    def wrapper(update: Update, *args, **kwargs):
        username = update.effective_user.username
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        if username or whitelisted(user_id, chat_id):
            func(update, *args, **kwargs)
    return wrapper


def admin(func):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        bot = context.bot

        if user_id in get_admin_ids(bot, chat_id):
            func(update, context, *args, **kwargs)
    return wrapper


def owner(func):
    def wrapper(update: Update, *args, **kwargs):
        if OWNER_ID and OWNER_ID == update.effective_user.id:
            func(update, *args, **kwargs)
    return wrapper