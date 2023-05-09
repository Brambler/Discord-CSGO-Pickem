# CSGO Pickem Discord Bot

This is a Discord bot that allows users to authorize their Steam account and display their CSGO Pick'Em Challenge predictions in Discord.

## Dependencies

This bot is written in Python and uses the following libraries:

- [discord.py](https://pypi.org/project/discord.py/)
- [redis](https://pypi.org/project/redis/)
- [requests](https://pypi.org/project/requests/)
- [typing](https://pypi.org/project/typing/)

## How to use

To use this bot, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Create a new Discord application and add a bot to it.
4. Copy the bot token and add it to an environment variable called `discordToken`.
5. Create a Redis database and add its URL to an environment variable called `REDISCLOUD_URL`.
6. Set the `steam_api_key` environment variable to your Steam API key.
7. Set the `event_id` environment variable to the ID of the CSGO Major event you want to display (e.g. "12345" for the 2023 Paris Major).
8. Set the `discordGuildID` environment variable to the ID of the Discord server where you want to use the bot.
9. Run the bot by running `python main.py`.

The bot responds to two commands:

- `/authorize`: This command prompts the user to enter their Steam profile URL and Pick'Em Challenge authentication code. The bot then saves the user's Steam ID and auth code to the Redis database.
- `/showpickem`: This command displays the user's current Pick'Em Challenge predictions.

Note that users must run the `/authorize` command before they can use the `/showpickem` command.

## Planned Features

- [ ] MultiStage Support (Challenger, Legends, Champions)

- [ ] Track Pickem Coin Points

## Demo of using the bot

https://github.com/Brambler/Discord-CSGO-Pickem/assets/25120419/28b95898-7f22-4fda-9ac3-9dda4749ca8f
