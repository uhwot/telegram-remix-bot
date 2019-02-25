from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
import time, os
from mwt import MWT

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

NAME = "appname"
TOKEN = "sikeyouthought"
PORT = os.environ.get('PORT')
updater = Updater(TOKEN)
# add handlers
updater.start_webhook(listen="0.0.0.0",
                      port=int(PORT),
                      url_path=TOKEN)
updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))

watchlist = []

@MWT(timeout=3600)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

@run_async
def check(bot, update):
    
    if (update.message.from_user.id in get_admin_ids(bot, update.message.chat_id)):
        print(update.effective_user.full_name + " is an admin.")
    else:
        
        if (update.effective_user.username == None):
            
            if (update.effective_user.id in watchlist):
                update.message.delete()
                print("Deleted message from " + update.effective_user.full_name)
            
            else:
                print(update.effective_user.full_name + " has no username. Waiting...")
                watchlist.append(update.effective_user.id)
                update.effective_chat.send_message(update.effective_user.full_name + ", please get a username in 2 minutes, or you will be kicked.")
                update.message.delete()
                
                time.sleep(120)
                
                if (update.effective_user.username == None):
                    
                    update.effective_chat.kick_member(update.effective_user.id)
                    update.effective_chat.unban_member(update.effective_user.id)
                    watchlist.remove(update.effective_user.id)
                    print(update.effective_user.full_name + " has been kicked.")
                    update.effective_chat.send_message(update.effective_user.full_name + " has been kicked.")
                
                else:
                    watchlist.remove(update.effective_user.id)
                    print(update.effective_user.full_name + " now has a username.")

updater.dispatcher.add_handler(MessageHandler(Filters.chat(-1001366985278), check))
print("Started.")
updater.idle()
