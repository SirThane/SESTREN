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
    "admin",
    "vc_access",
]

description = "Testing vc_access"

try:
    with open('auth.json', 'r+') as auth_file:
        auth = json.load(auth_file)
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
    print()
    for extension in initial_extensions:
        try:
            print('Loading initial cog {}'.format(extension))
            bot.load_extension('cogs.{}'.format(extension))
            # log.info("Loaded {}".format(extension))
        except Exception as e:
            # log.warning('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    print()
    bot.run(token, bot=True)
