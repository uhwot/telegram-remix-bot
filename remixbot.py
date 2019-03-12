from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram import ParseMode
import time, os, random
from mwt import MWT
from slap_msgs import SLAP_TEMPLATES, ITEMS, THROW, HIT

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

NAME = os.environ.get("APPNAME")
TOKEN = os.environ.get("TOKEN")
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
    
    if (update.effective_user.id in get_admin_ids(bot, update.message.chat_id)):
        print(update.effective_user.full_name + " is an admin.")
    else:
        
        if (update.effective_user.username == None):
            
            if (update.effective_user.id in watchlist):
                update.message.delete()
                print("Deleted message from " + update.effective_user.full_name)
            
            else:
                print(update.effective_user.full_name + " has no username. Waiting...")
                watchlist.append(update.effective_user.id)
                msg_id = update.effective_chat.send_message(update.effective_user.full_name + ", please get a username in 2 minutes, or you will be kicked.")["message_id"]
                update.message.delete()
                
                time.sleep(120)
                
                bot.delete_message(update.effective_chat.id, msg_id)

                if (update.effective_chat.get_member(update.effective_user.id)["user"]["username"] == None):
                    
                    update.effective_chat.kick_member(update.effective_user.id)
                    update.effective_chat.unban_member(update.effective_user.id)
                    watchlist.remove(update.effective_user.id)
                    print(update.effective_user.full_name + " has been kicked.")
                    msg_id = update.effective_chat.send_message(update.effective_user.full_name + " has been kicked.")["message_id"]
                    time.sleep(120)
                    bot.delete_message(update.effective_chat.id, msg_id)
                
                else:
                    watchlist.remove(update.effective_user.id)
                    print(update.effective_user.full_name + " now has a username.")

def slap(bot, update):
    if ((update.message.text).startswith("#slap")):
        
        if (update.effective_user.username != None):
            
            if (update.effective_message.reply_to_message != None):
                
                if (update.effective_message.reply_to_message.from_user.id == 760807185):
                    update.effective_message.reply_text("Nah.")
                    return
                
                user2 = ("[{}](tg://user?id={})").format(update.effective_message.reply_to_message.from_user.full_name, update.effective_message.reply_to_message.from_user.id)
                
                reply = True
            else:
                
                user2 = (update.message.text).split()
                
                try:
                    user2[1]
                except IndexError:
                    update.effective_message.reply_text("Reply to a message or type a username to use this command!")
                    return
                
                if (user2[1].startswith("@")):
                    user2 = user2[1]
                else:
                    user2 = "@" + user2[1]
                
                if ((user2 == "@admin") | ("/" in user2)):
                    update.effective_message.delete()
                    return
                if (user2 == "@deezremix_bot"):
                    update.effective_message.reply_text("Nah.")
                    return
                if ((len(user2) < 6) | (len(user2) > 33)):
                    update.effective_message.reply_text("That user doesn't exist! This command only works with usernames and replies.")
                    return
                
                reply = False
            
            temp = random.choice(SLAP_TEMPLATES)
            item = random.choice(ITEMS)
            hit = random.choice(HIT)
            throw = random.choice(THROW)
            
            user1 = ("[{}](tg://user?id={})").format(update.effective_user.full_name, update.effective_user.id)
            
            if(reply == True):
                update.effective_chat.send_message(temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw), ParseMode.MARKDOWN, reply_to_message_id=update.message.reply_to_message.message_id)
            else:
                update.effective_message.reply_markdown(temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw))

updater.dispatcher.add_handler(MessageHandler(Filters.chat(-1001366985278), check))
updater.dispatcher.add_handler(MessageHandler((Filters.chat(-1001366985278) & Filters.text), slap), -1)
print("Started.")
updater.idle()
