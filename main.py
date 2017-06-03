"""
Currently a test bot.
"""

import json
import sys
from discord.ext import commands
import discord
import asyncio
import traceback

prefix = ["$"]

initial_extensions = [
    "cogs.admin",
    "cogs.utils.vc_update"
]

description = "Testing vc_access"

try:
    with open('auth.json', 'r+') as json_auth_info:
        auth = json.load(json_auth_info)
        token = auth["discord"]["token"]
except IOError:
    sys.exit("auth.json not found in running directory.")

bot = commands.Bot(command_prefix=prefix, description=description, pm_help=True, self_bot=False)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    # log.info("Initialized.")

    print('------')


@bot.event
async def on_message(message):
    await bot.process_commands(message)


# bot.config = Config("config.json")

# Starting up

if __name__ == "__main__":
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            # log.info("Loaded {}".format(extension))
        except Exception as e:
            # log.warning('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

        bot.run(token, bot=True)
