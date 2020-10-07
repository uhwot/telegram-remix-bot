import logging

from telegram.ext import (
    CallbackContext,
    PrefixHandler,
    MessageHandler,
    Filters,
)
from telegram import Update, ParseMode
from telegram.error import BadRequest

from .. import dispatcher
from ..utils import get_id, insert_user, delete, group_id, admin, add_help


@group_id
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


USERLOGGER_HANDLER = MessageHandler(Filters.group, user_logger, run_async=True)
dispatcher.add_handler(USERLOGGER_HANDLER, 1)
