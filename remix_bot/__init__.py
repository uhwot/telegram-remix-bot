import os
import logging

from telegram.ext import Updater

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = os.environ.get("TOKEN")
# optional vars
GROUP_ID = os.environ.get("GROUP_ID")
if GROUP_ID:
    GROUP_ID = GROUP_ID.split()
OWNER_ID = os.environ.get("OWNER_ID")
if OWNER_ID:
    OWNER_ID = int(OWNER_ID)
# webhooks
URL = os.environ.get("URL")
PORT = os.environ.get("PORT")
CERT_PATH = os.environ.get("CERT_PATH")
# database
DB_URL = os.environ.get("DB_URL")


updater = Updater(TOKEN)
dispatcher = updater.dispatcher
