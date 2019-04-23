import time
import os
import random
import logging
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from telegram.error import BadRequest
from mwt import MWT
from slap_msgs import SLAP_TEMPLATES, SLAP_SELF, SLAP_BASIC, ITEMS, THROW, HIT

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

TOKEN = os.environ.get("TOKEN")
# optional vars
GROUP_ID = os.environ.get("GROUP_ID")
URL = os.environ.get("URL")

updater = Updater(TOKEN)
dispatcher = updater.dispatcher

if URL:
    PORT = os.environ.get("PORT")
    
    updater.start_webhook(listen="0.0.0.0",
                        port=int(PORT),
                        url_path=TOKEN)
    updater.bot.set_webhook(URL + TOKEN)

watchlist = []

@MWT(timeout=3600)
def get_admin_ids(bot, chat_id):
    # Returns a list of admin IDs for a given chat. Results are cached for 1 hour.
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

@run_async
def check(bot, update):
    
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    
    guide = "https://gitlab.com/uh_hey/telegram-remix-bot/wikis/How-to-set-a-username"
    
    if user.id in get_admin_ids(bot, chat.id):
        print(user.full_name + " is an admin.")
    else:
        
        if not user.username:
            
            if user.id in watchlist:
                message.delete()
                print("Deleted message from " + user.full_name)
            
            else:
                print(user.full_name + " has no username. Waiting...")
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
                    print(user.full_name + " has been kicked.")
                    msg_id = chat.send_message(escape_markdown(user.full_name) + " has been kicked.")["message_id"]
                    time.sleep(120)
                    bot.delete_message(chat.id, msg_id)
                
                else:
                    watchlist.remove(user.id)
                    print(user.full_name + " now has a username or has left.")

@run_async
def slap(bot, update):
    
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat
    
    if (message.text).startswith("#slap"):
        
        if user.username:
            
            user1 = ("[{}](tg://user?id={})").format(user.full_name, user.id)
            user2 = None
            self = False
            basic = False
            
            if message.reply_to_message:
                
                if message.reply_to_message.from_user.id == bot.id:
                    message.reply_text("Nah.")
                    return
                
                if user.id == message.reply_to_message.from_user.id:
                    self = True
                else:
                    user2 = ("[{}](tg://user?id={})").format(message.reply_to_message.from_user.full_name, message.reply_to_message.from_user.id)
                
                reply_msg = message.reply_to_message.message_id
            else:
                
                user2 = message.text.split()
                
                try:
                    user2[1]
                except IndexError:
                    basic = True
                    
                else:
                    
                    if user2[1].startswith("@"):
                        user2 = user2[1]
                    else:
                        user2 = "@" + user2[1]
                    
                    if user2 == "@admin" or "/" in user2:
                        message.delete()
                        return
                    if user2[1:] == bot.username:
                        message.reply_text("Nah.")
                        return
                    if user2[1:] == user.username:
                        self = True
                    else:
                        
                        if len(user2) < 6 or len(user2) > 33:
                            message.reply_text("That user doesn't exist!")
                            return
                        
                        user2 = escape_markdown(user2)
                
                reply_msg = message.message_id
            
            if self:
                temp = random.choice(SLAP_SELF)
            elif basic:
                temp = random.choice(SLAP_BASIC)
            else:
                temp = random.choice(SLAP_TEMPLATES)
            
            item = random.choice(ITEMS)
            hit = random.choice(HIT)
            throw = random.choice(THROW)
            
            chat.send_message(temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw), ParseMode.MARKDOWN, reply_to_message_id=reply_msg)

if GROUP_ID:
    check_handler = MessageHandler(Filters.chat(int(GROUP_ID)) and Filters.group, check)
    slap_handler = MessageHandler(Filters.chat(int(GROUP_ID)) and Filters.group and Filters.text, slap)
else:
    check_handler = MessageHandler(Filters.group, check)
    slap_handler = MessageHandler(Filters.group and Filters.text, slap)
    
dispatcher.add_handler(check_handler)
dispatcher.add_handler(slap_handler, 1)

if not URL:
    updater.start_polling()

print("Started.")
updater.idle()
