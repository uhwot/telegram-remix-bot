# telegram-remix-bot

Some random Telegram bot made with a bunch of spaghetti code.

Made for the [@deemixCommunity](https://t.me/deemixCommunity) group.

# how 2 setup

1. Set these environment variables:

- `TOKEN`: Your bot token from [@BotFather](https://t.me/BotFather).

- `GROUP_ID` (optional): The ID of the group where the bot should run. You can also specify multiple IDs by separating them with spaces. If not set, the bot will work in all groups.

- `OWNER_ID` (optional): The ID of the bot owner. Required for `#send` and `#sendall`.

- `URL` (webhooks): The URL your webhook should connect to. If not set, the bot will use long polling instead.

- `PORT` (webhooks): Port to use for your webhooks.

- `CERT_PATH` (webhooks): Path to your webhook certificate.

- `DB_URL` (database): Your MongoDB database URL. If not set, the username logger won't be available.

2. Move to the bot directory (hint: cd)

3. Install the dependencies:

- `pip3 install -r requirements.txt`

# how 2 run

1. Move to the bot directory (hint: cd)

2. Run: `python3 -m remix_bot`
