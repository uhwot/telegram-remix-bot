from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram import ParseMode
import time, os, random
from mwt import MWT
from slap_msgs import SLAP_TEMPLATES, ITEMS, THROW, HIT

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

URL = os.environ.get("URL")
TOKEN = os.environ.get("TOKEN")
PORT = os.environ.get("PORT")
GROUP_ID = os.environ.get("GROUP_ID")

updater = Updater(TOKEN)
# add handlers
updater.start_webhook(listen="0.0.0.0",
                      port=int(PORT),
                      url_path=TOKEN)
updater.bot.set_webhook(URL + TOKEN)

watchlist = []

@MWT(timeout=3600)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

@run_async
def check(bot, update):
    
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    
    if (user.id in get_admin_ids(bot, chat.id)):
        print(user.full_name + " is an admin.")
    else:
        
        if (user.username == None):
            
            if (user.id in watchlist):
                message.delete()
                print("Deleted message from " + user.full_name)
            
            else:
                print(user.full_name + " has no username. Waiting...")
                watchlist.append(user.id)
                msg_id = chat.send_message(user.full_name + ", please [get a username](https://gitlab.com/uh_hey/telegram-remix-bot/wikis/How-to-set-a-username) in 2 minutes or you will be kicked.", ParseMode.MARKDOWN)["message_id"]
                message.delete()
                
                time.sleep(120)
                
                bot.delete_message(chat.id, msg_id)

                if (chat.get_member(user.id)["user"]["username"] == None):
                    
                    chat.kick_member(user.id)
                    chat.unban_member(user.id)
                    print(user.full_name + " has been kicked.")
                    msg_id = chat.send_message(user.full_name + " has been kicked.")["message_id"]
                    time.sleep(120)
                    bot.delete_message(chat.id, msg_id)
                
                else:
                    print(update.effective_user.full_name + " now has a username.")
                
                watchlist.remove(user.id)

def slap(bot, update):
    
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    
    if ((message.text).startswith("#slap")):
        
        if (user.username != None):
            
            if (message.reply_to_message != None):
                
                if (message.reply_to_message.from_user.id == bot.id):
                    message.reply_text("Nah.")
                    return
                
                user2 = ("[{}](tg://user?id={})").format(message.reply_to_message.from_user.full_name, message.reply_to_message.from_user.id)
                
                reply_msg = message.reply_to_message.message_id
            else:
                
                user2 = (message.text).split()
                
                try:
                    user2[1]
                except IndexError:
                    message.reply_text("Reply to a message or type a username to use this command!")
                    return
                
                if (user2[1].startswith("@")):
                    user2 = user2[1]
                else:
                    user2 = "@" + user2[1]
                
                if ((user2 == "@admin") | ("/" in user2)):
                    message.delete()
                    return
                if (user2[1:] == bot.username):
                    message.reply_text("Nah.")
                    return
                if ((len(user2) < 6) | (len(user2) > 33)):
                    message.reply_text("That user doesn't exist! This command only works with usernames and replies.")
                    return
                
                reply_msg = message.message_id
            
            temp = random.choice(SLAP_TEMPLATES)
            item = random.choice(ITEMS)
            hit = random.choice(HIT)
            throw = random.choice(THROW)
            
            user1 = ("[{}](tg://user?id={})").format(user.full_name, user.id)
            
            chat.send_message(temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw), ParseMode.MARKDOWN, reply_to_message_id=reply_msg)

if GROUP_ID:
    updater.dispatcher.add_handler(MessageHandler((Filters.chat(int(GROUP_ID)) & Filters.group), check))
    updater.dispatcher.add_handler(MessageHandler((Filters.chat(int(GROUP_ID)) & Filters.group & Filters.text), slap), -1)
else:
    updater.dispatcher.add_handler(MessageHandler(Filters.group, check))
    updater.dispatcher.add_handler(MessageHandler((Filters.group & Filters.text), slap), -1)

print("Started.")
updater.idle()