import pymongo
import re

from remix_bot import DB_URL
from remix_bot.mwt import MWT

db_client = pymongo.MongoClient(DB_URL)
whitelist_db = db_client["whitelist"]

global_db = db_client["global"]
userlog = global_db["users"]


@MWT(timeout=3600)
def get_admin_ids(bot, chat_id):
    # Returns a list of admin IDs for a given chat. Results are cached for 1 hour.
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


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
