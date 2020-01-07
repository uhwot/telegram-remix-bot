import logging

from time import sleep
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, run_async, MessageHandler, Filters

from .. import dispatcher
from ..utils import get_admin_ids, build_menu, whitelisted, group_id, delete

watchlist = []


@run_async
@group_id
def check(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    bot = context.bot

    guide = "https://gitlab.com/uh_wot/telegram-remix-bot/wikis/How-to-set-a-username"
    
    if user.id == 777000:  # channel messages
        return
    
    if user.id in get_admin_ids(bot, chat.id):
        logging.info(f"{user.full_name} is an admin.")
        return

    if whitelisted(user.id, chat.id):
        logging.info(f"{user.full_name} is in the whitelist.")
        return

    if user.username:
        return

    if user.id in watchlist:
        delete(message)
        logging.info(f"Deleted message from {user.full_name}")
        return

    logging.info(f"{user.full_name} has no username. Waiting...")
    watchlist.append(user.id)

    temp = f"{user.full_name}, set a username in 2 minutes or you will be kicked."
    button = [InlineKeyboardButton("How to set a username", url=guide)]
    reply_markup = InlineKeyboardMarkup(build_menu(button, n_cols=1))

    temp_msg = chat.send_message(temp, reply_markup=reply_markup)

    if not message.new_chat_members:
        delete(message)

    sleep(120)

    delete(temp_msg)

    if not chat.get_member(user.id)["user"]["username"] \
    and chat.get_member(user.id)["status"] not in ("left", "kicked"):

        chat.unban_member(user.id)  # unban on user = kick
        watchlist.remove(user.id)
        logging.info(f"{user.full_name} has been kicked.")
        temp_msg = chat.send_message(f"{user.full_name} has been kicked.")
        sleep(120)
        delete(temp_msg)

    else:
        watchlist.remove(user.id)
        logging.info(f"{user.full_name} now has a username or has left.")


check_handler = MessageHandler(Filters.group, check)

dispatcher.add_handler(check_handler, 1)
