import time
import logging

from telegram import ParseMode
from telegram.ext import run_async, MessageHandler, Filters
from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown

from remix_bot import GROUP_ID, DB_URL, dispatcher, get_admin_ids, whitelisted

watchlist = []


@run_async
def check(bot, update):

    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat

    guide = "https://gitlab.com/uh_wot/telegram-remix-bot/wikis/How-to-set-a-username"

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
    msg_id = chat.send_message("{}, please [get a username]({}) in 2 minutes or you will be kicked.".format(escape_markdown(user.full_name), guide), ParseMode.MARKDOWN)["message_id"]

    if not message.new_chat_members:
        try:
            message.delete()
        except BadRequest:
            pass

    time.sleep(120)

    bot.delete_message(chat.id, msg_id)

    if not chat.get_member(user.id)["user"]["username"] \
    and chat.get_member(user.id)["status"] not in ("left", "kicked"):

        chat.unban_member(user.id) # unban on user = kick
        watchlist.remove(user.id)
        logging.info(user.full_name + " has been kicked.")
        msg_id = chat.send_message(escape_markdown(user.full_name) + " has been kicked.")["message_id"]
        time.sleep(120)
        bot.delete_message(chat.id, msg_id)

    else:
        watchlist.remove(user.id)
        logging.info(user.full_name + " now has a username or has left.")


if GROUP_ID:
    check_handler = MessageHandler(Filters.chat(int(GROUP_ID)) & Filters.group, check)
else:
    check_handler = MessageHandler(Filters.group, check)

dispatcher.add_handler(check_handler)
