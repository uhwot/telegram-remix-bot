import logging

from remix_bot import updater, dispatcher
from remix_bot import TOKEN, GROUP_ID, URL, PORT, CERT_PATH, DB_URL

if URL:
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    if CERT_PATH:
        updater.bot.set_webhook(URL + TOKEN,
                                certificate=open(CERT_PATH, "rb"))
    else:
        updater.bot.set_webhook(URL + TOKEN)

import remix_bot.username_check
import remix_bot.fun
if DB_URL:
    import remix_bot.database


if not URL:
    updater.start_polling()

logging.info("Started.")
