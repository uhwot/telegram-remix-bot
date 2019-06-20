import logging

from remix_bot import updater
from remix_bot import TOKEN, URL, PORT, CERT_PATH, DB_URL

if URL:
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    if CERT_PATH:
        logging.info("Webhooks with HTTPS certificate enabled.")
        updater.bot.set_webhook(URL + TOKEN,
                                certificate=open(CERT_PATH, "rb"))

    else:
        logging.info("Webhooks without HTTPS certificate enabled.")
        updater.bot.set_webhook(URL + TOKEN)

else:
    logging.info("Webhooks disabled, using long polling instead.")

import remix_bot.modules.username_check
import remix_bot.modules.fun
if DB_URL:
    logging.info("Database enabled.")
    import remix_bot.modules.database
else:
    logging.info("Database disabled.")


if not URL:
    updater.start_polling()

logging.info("Started.")
updater.idle()

