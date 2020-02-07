from telegram import Update, ParseMode
from telegram.ext import CallbackContext, run_async, PrefixHandler, Filters

from .. import dispatcher
from ..utils import group_id, username, add_help
from .. import utils

@run_async
@group_id
@username
def help(update: Update, context: CallbackContext):
    message = update.effective_message

    msg = ""
    for cmd, desc in utils.cmds.items():
        msg += f"• {cmd}: {desc}\n"
    
    message.reply_text(msg, ParseMode.MARKDOWN)


help_handler = PrefixHandler("#", "help", help, Filters.group)
dispatcher.add_handler(help_handler)
add_help("help", "Shows a list of commands and their descriptions.")