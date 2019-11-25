import random

from telegram import Update, ParseMode
from telegram.ext import CallbackContext, run_async, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown
from telegram.error import BadRequest

from .. import DB_URL, dispatcher, OWNER_ID, GROUP_ID
from ..utils import whitelisted, get_id, get_name, group_id_filter, delete
from ..slap_msgs import *


@run_async
def slap(update: Update, context: CallbackContext):

    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    bot = context.bot

    if not user.username and not whitelisted(user.id, chat.id):
        return

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

    chat.send_message(temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw), ParseMode.MARKDOWN, reply_to_message_id=reply_msg)


@run_async
def runs(update: Update, _):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not user.username and not whitelisted(user.id, chat.id):
        return

    message.reply_text(random.choice(RUN_STRINGS))


@run_async
def send(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message
    bot = context.bot

    split = message.text.split()

    if not OWNER_ID:
        return

    if OWNER_ID != user.id:
        return

    if split[0] == "#send":
        try:
            chat_ids = [int(split[1])]
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

    if split[0] == "#send":
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
    else:
        message.reply_text("Messages sent!")


slap_handler = MessageHandler(Filters.regex(r"^#slap(\s|$)") & group_id_filter & Filters.group & Filters.text, slap)
runs_handler = MessageHandler(Filters.regex(r"^#runs(\s|$)") & group_id_filter & Filters.group & Filters.text, runs)
send_handler = MessageHandler(Filters.regex(r"^#send(all)?(\s|$)") & Filters.private & Filters.text, send)

dispatcher.add_handler(slap_handler)
dispatcher.add_handler(runs_handler)
dispatcher.add_handler(send_handler)
