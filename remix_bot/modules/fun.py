import random

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, run_async, PrefixHandler, Filters
from telegram.utils.helpers import escape_markdown
from telegram.error import BadRequest, Unauthorized

from .. import DB_URL, dispatcher, OWNER_ID, GROUP_ID
from ..utils import get_id, get_name, group_id, delete, username, owner, add_help
from ..slap_msgs import *


@run_async
@group_id
@username
def slap(update: Update, context: CallbackContext):
    update.effective_message.reply_text("i won't slap for u, ur too gay")


@run_async
@group_id
@username
def runs(update: Update, _):
    update.effective_message.reply_text("bruh y u running")


@run_async
@owner
def send(update: Update, context: CallbackContext):
    message = update.effective_message
    bot = context.bot
    args = context.args

    cmd = message.text.split()[0]

    if cmd == "#send":
        try:
            chat_ids = [int(args[0])]
        except ValueError:
            message.reply_text("Invalid chat ID.")
            return
        except IndexError:
            message.reply_text("Please specify a chat ID.")
            return
    elif GROUP_ID:
        chat_ids = GROUP_ID
    else:
        message.reply_text("Env variable GROUP_ID not specified.")
        return

    if cmd == "#send":
        split_num = 2
    else:
        split_num = 1

    try:
        text = message.text.split(" ", split_num)[split_num]
    except IndexError:
        message.reply_text("Please specify some text.")
        return

    try:
        for id in chat_ids:
            bot.send_message(id, text)
    except BadRequest:
        message.reply_text("Couldn't send all messages.")
    except Unauthorized:
        message.reply_text(
            "Request unauthorized. Are you trying to send a message to a bot?"
        )
    else:
        message.reply_text("Messages sent!")


SLAP_HANDLER = PrefixHandler("#", "slap", slap, Filters.group)
RUNS_HANDLER = PrefixHandler("#", "runs", runs, Filters.group)
SEND_HANDLER = PrefixHandler("#", ["send", "sendall"], send, Filters.private)

dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SEND_HANDLER)

add_help("slap", "Slaps a user.")
add_help("runs", "Why are you running?")
add_help(
    "send/sendall", "Sends a message to specified groups or users.", owner_only=True
)

