import random

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, run_async, PrefixHandler, Filters
from telegram.utils.helpers import escape_markdown
from telegram.error import BadRequest, Unauthorized

from .. import DB_URL, dispatcher, OWNER_ID, GROUP_ID
from ..utils import get_id, get_name, group_id, delete, owner, add_help
from ..slap_msgs import *


@group_id
def slap(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    bot = context.bot

    user1 = f"[{user.full_name}](tg://user?id={user.id})"
    user2 = None
    self = False
    basic = False

    if message.reply_to_message:

        if message.reply_to_message.from_user.id == bot.id:
            message.reply_text("Nah.")
            return

        if user.id == message.reply_to_message.from_user.id:
            self = True
        else:
            user2 = f"[{message.reply_to_message.from_user.full_name}](tg://user?id={message.reply_to_message.from_user.id})"

        reply_msg = message.reply_to_message.message_id
    else:

        try:
            user2 = message.parse_entity(message.entities[1])[1:]
        except IndexError:
            basic = True
        else:

            temp = user2.lower()

            if temp == "admin" or "/" in temp:
                delete(message)
                return
            if temp == bot.username.lower():
                message.reply_text("Nah.")
                return
            if temp == user.username.lower():
                self = True
            else:

                if DB_URL:
                    try:
                        user2 = f"[{get_name(user2)}](tg://user?id={get_id(user2)})"
                    except KeyError:
                        user2 = "@" + escape_markdown(user2)
                else:
                    user2 = "@" + escape_markdown(user2)

        reply_msg = message.message_id

    if self:
        temp = random.choice(SLAP_SELF)
    elif basic:
        temp = random.choice(SLAP_BASIC)
    else:
        temp = random.choice(SLAP_TEMPLATES)

    item = random.choice(ITEMS)
    hit = random.choice(HIT)
    throw = random.choice(THROW)

    chat.send_message(
        temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw),
        ParseMode.MARKDOWN,
        reply_to_message_id=reply_msg,
    )


@group_id
def runs(update: Update, _):
    update.effective_message.reply_text(random.choice(RUN_STRINGS))


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


SLAP_HANDLER = PrefixHandler("#", "slap", slap, Filters.group, run_async=True)
RUNS_HANDLER = PrefixHandler("#", "runs", runs, Filters.group, run_async=True)
SEND_HANDLER = PrefixHandler("#", ["send", "sendall"], send, Filters.private, run_async=True)

dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SEND_HANDLER)

add_help("slap", "Slaps a user.")
add_help("runs", "Why are you running?")
add_help(
    "send/sendall", "Sends a message to specified groups or users.", owner_only=True
)

