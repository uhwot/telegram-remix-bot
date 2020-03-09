import logging
from importlib import import_module

from . import updater
from . import TOKEN, URL, PORT, CERT_PATH, DB_URL
from .modules import ALL_MODULES

if URL:
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    if CERT_PATH:
        logging.info("Webhooks with HTTPS certificate enabled.")
        updater.bot.set_webhook(URL + TOKEN, certificate=open(CERT_PATH, "rb"))

    else:
        logging.info("Webhooks without HTTPS certificate enabled.")
        updater.bot.set_webhook(URL + TOKEN)

else:
    logging.info("Webhooks disabled, using long polling instead.")

disabled_modules = []
if not DB_URL:
    logging.info("Database disabled.")
    disabled_modules.append("database")
else:
    logging.info("Database enabled.")

for module in disabled_modules:
    ALL_MODULES.remove(module)

for module in ALL_MODULES:
    import_module("remix_bot.modules." + module)

if not URL:
    updater.start_polling()

logging.info("Started.")
updater.idle()
