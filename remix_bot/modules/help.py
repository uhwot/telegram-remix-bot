from telegram import Update
from telegram.ext import CallbackContext, PrefixHandler, Filters

from .. import dispatcher
from ..utils import group_id, add_help
from .. import utils


@group_id
def help(update: Update, context: CallbackContext):
    message = update.effective_message

    msg = ""
    for cmd, desc in utils.cmds.items():
        msg += f"• {cmd}: {desc}\n"

    message.reply_text(msg)


HELP_HANDLER = PrefixHandler("#", "help", help, Filters.chat_type.groups, run_async=True)
dispatcher.add_handler(HELP_HANDLER)
add_help("help", "Shows a list of commands and their descriptions.")
