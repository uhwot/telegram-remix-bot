# telegram-remix-bot

Some random Telegram bot made with a bunch of spaghetti code that kicks people who don't have usernames.

Made for the [@DeezloaderRemixCommunity](https://t.me/DeezloaderRemixCommunity) group.

# how 2 setup

1. Set these environment variables:

- `TOKEN`: Your bot token from [@BotFather](https://t.me/BotFather).

- `GROUP_ID` (optional): The ID of the group where the bot should run. If not set, the bot will work in all groups.

- `URL` (optional): The URL your webhook should connect to. If not set, the bot will use long polling instead.

- `PORT` (optional): Port to use for your webhooks.

2. Move to the bot directory (hint: cd)

3. Install the dependencies:

- `pip3 install -r requirements.txt`

# how 2 run

1. Move to the bot directory (hint: cd)

2. Run: `python3 remixbot.py`
