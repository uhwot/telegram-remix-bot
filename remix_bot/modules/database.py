import logging

from telegram.ext import CallbackContext, MessageHandler, Filters, run_async
from telegram import Update, ParseMode
from telegram.error import BadRequest

from .. import dispatcher
from ..utils import get_admin_ids, get_id, whitelist_db, insert_user, group_id_filter, delete


@run_async
def whitelist_check(update: Update, context: CallbackContext):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot = context.bot

    if not message.text.split()[0] == "#whitelist":
        return

    if user.id not in get_admin_ids(bot, chat.id):
        delete(message)
        return

    whitelist = whitelist_db[str(chat.id)]
    ids = []

    for doc in whitelist.find():
        ids.append(doc["id"])

    msg = "Current whitelist:"

    for id in ids:
        curr_user = chat.get_member(id)["user"]
        msg = msg + f"\n[{curr_user.full_name}](tg://user?id={id}): {id}"

    message.reply_text(msg, ParseMode.MARKDOWN)


@run_async
def whitelist_mngr(update: Update, context: CallbackContext):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot = context.bot

    if message.text.split()[0] not in ("#addwhitelist", "#rmwhitelist"):
        return

    if user.id not in get_admin_ids(bot, chat.id):
        delete(message)
        return

    try:
        whitelisted_user = message.entities[1]["user"]
    except IndexError:
        message.reply_text("Mention a user to use this command.")
        return

    if not whitelisted_user:

        entity_text = message.parse_entity(message.entities[1])

        try:
            whitelisted_user = chat.get_member(get_id(entity_text[1:]))["user"]
        except KeyError:
            if entity_text.startswith("@"):
                message.reply_text("That username isn't in the database. Try again with a user ID.")
                return

            try:
                whitelisted_user = chat.get_member(entity_text)["user"]
            except BadRequest:
                message.reply_text("That user isn't in this group.")
                return

        except BadRequest:
            message.reply_text("That user isn't in this group.")
            return

    whitelist = whitelist_db[str(chat.id)]
    user_dict = {"id": whitelisted_user.id}

    if message.text.split()[0] == "#addwhitelist":
        whitelist.replace_one(user_dict, user_dict, True)
        message.reply_text(f"Added {whitelisted_user.full_name} to the whitelist!")
        logging.info(f"{user.full_name} added {whitelisted_user.full_name} to the whitelist!")
    else:
        whitelist.delete_one(user_dict)
        message.reply_text(f"Removed {whitelisted_user.full_name} from the whitelist!")
        logging.info(f"{user.full_name} removed {whitelisted_user.full_name} from the whitelist!")


@run_async
def user_logger(update: Update, context: CallbackContext):
    # This function inserts user IDs, usernames and names to the database to handle usernames.
    # This is due to Bot API limitations.

    message = update.effective_message
    user = update.effective_user

    if user.username:
        insert_user(user.id, user.username, user.full_name)

    if message.reply_to_message:
        if message.reply_to_message.from_user.username:
            replied_user = message.reply_to_message.from_user
            insert_user(replied_user.id, replied_user.username, replied_user.full_name)

    if message.forward_from:
        if message.forward_from.username:
            forward_from = message.forward_from
            insert_user(forward_from.id, forward_from.username, forward_from.full_name)


whitelistmngr_handler = MessageHandler(group_id_filter & Filters.group & Filters.text, whitelist_mngr)
whitelist_handler = MessageHandler(group_id_filter & Filters.group & Filters.text, whitelist_check)
userlogger_handler = MessageHandler(group_id_filter & Filters.group, user_logger)

dispatcher.add_handler(userlogger_handler, 3)
dispatcher.add_handler(whitelistmngr_handler, 4)
dispatcher.add_handler(whitelist_handler, 5)
