import time
import logging

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, run_async, MessageHandler, Filters
from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown

from .. import dispatcher
from ..utils import get_admin_ids, build_menu, whitelisted, group_id_filter

watchlist = []


@run_async
def check(update: Update, context: CallbackContext):

    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    bot = context.bot

    guide = "https://gitlab.com/uh_wot/telegram-remix-bot/wikis/How-to-set-a-username"
    
    if user.id == 777000:  # channel messages
        return
    
    if user.id in get_admin_ids(bot, chat.id):
        logging.info(user.full_name + " is an admin.")
        return

    if whitelisted(user.id, chat.id):
        logging.info(user.full_name + " is in the whitelist.")
        return

    if user.username:
        return

    if user.id in watchlist:
        message.delete()
        logging.info("Deleted message from " + user.full_name)
        return

    logging.info(user.full_name + " has no username. Waiting...")
    watchlist.append(user.id)

    temp = escape_markdown(user.full_name) + ", get a username in 2 minutes or you will be kicked."
    button = [InlineKeyboardButton("How to set a username", url=guide)]
    reply_markup = InlineKeyboardMarkup(build_menu(button, n_cols=1))

    msg_id = chat.send_message(temp, ParseMode.MARKDOWN, reply_markup=reply_markup)["message_id"]

    if not message.new_chat_members:
        try:
            message.delete()
        except BadRequest:
            pass

    time.sleep(120)

    bot.delete_message(chat.id, msg_id)

    if not chat.get_member(user.id)["user"]["username"] \
    and chat.get_member(user.id)["status"] not in ("left", "kicked"):

        chat.unban_member(user.id)  # unban on user = kick
        watchlist.remove(user.id)
        logging.info(user.full_name + " has been kicked.")
        msg_id = chat.send_message(escape_markdown(user.full_name) + " has been kicked.")["message_id"]
        time.sleep(120)
        bot.delete_message(chat.id, msg_id)

    else:
        watchlist.remove(user.id)
        logging.info(user.full_name + " now has a username or has left.")


check_handler = MessageHandler(group_id_filter & Filters.group, check)

dispatcher.add_handler(check_handler)
