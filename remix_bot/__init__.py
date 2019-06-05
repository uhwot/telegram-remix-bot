import os
import logging
import pymongo
import re

from telegram.ext import Updater

from remix_bot.mwt import MWT

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

TOKEN = os.environ.get("TOKEN")
# optional vars
GROUP_ID = os.environ.get("GROUP_ID")
# webhooks
URL = os.environ.get("URL")
PORT = os.environ.get("PORT")
CERT_PATH = os.environ.get("CERT_PATH")
# database
DB_URL = os.environ.get("DB_URL")


updater = Updater(TOKEN)
dispatcher = updater.dispatcher


db_client = pymongo.MongoClient(DB_URL)
whitelist_db = db_client["whitelist"]

global_db = db_client["global"]
userlog = global_db["users"]


@MWT(timeout=3600)
def get_admin_ids(bot, chat_id):
    # Returns a list of admin IDs for a given chat. Results are cached for 1 hour.
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


def get_id(username):
    try:
        temp = userlog.find_one({"username": re.compile(username, re.IGNORECASE)}, {"id": 1})["id"]
    except TypeError:
        raise KeyError
    else:
        return temp


def get_name(username):
    try:
        temp = userlog.find_one({"username": re.compile(username, re.IGNORECASE)}, {"name": 1})["name"]
    except TypeError:
        raise KeyError
    else:
        return temp


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
