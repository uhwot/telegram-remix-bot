import random

from telegram import ParseMode
from telegram.ext import run_async, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown

from remix_bot import DB_URL, GROUP_ID, whitelisted, get_id, get_name, dispatcher
from remix_bot.slap_msgs import *


@run_async
def slap(bot, update):

    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat

    if not message.text.split()[0] == "#slap":
        return

    if not user.username and not whitelisted(user.id, chat.id):
        return

    user1 = "[{}](tg://user?id={})".format(user.full_name, user.id)
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
            user2 = "[{}](tg://user?id={})".format(message.reply_to_message.from_user.full_name,
                                                   message.reply_to_message.from_user.id)

        reply_msg = message.reply_to_message.message_id
    else:

        try:
            user2 = message.parse_entity(message.entities[1])[1:]
        except IndexError:
            basic = True
        else:

            if user2 == "admin" or "/" in user2:
                message.delete()
                return
            if user2 == bot.username:
                message.reply_text("Nah.")
                return
            if user2 == user.username:
                self = True
            else:

                if DB_URL:
                    try:
                        user2 = "[{}](tg://user?id={})".format(get_name(user2), get_id(user2))
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
def runs(bot, update):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message.text.split()[0] == "#runs":
        return

    if not user.username and not whitelisted(user.id, chat.id):
        return

    message.reply_text(random.choice(RUN_STRINGS))


if GROUP_ID:
    slap_handler = MessageHandler(Filters.chat(int(GROUP_ID)) & Filters.group & Filters.text, slap)
    runs_handler = MessageHandler(Filters.chat(int(GROUP_ID)) & Filters.group & Filters.text, runs)
else:
    slap_handler = MessageHandler(Filters.group & Filters.text, slap)
    runs_handler = MessageHandler(Filters.group & Filters.text, runs)

dispatcher.add_handler(slap_handler, 1)
dispatcher.add_handler(runs_handler, 2)
