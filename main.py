"""
Currently a test bot.
Still a test bot
"""

import json
import sys
from discord.ext import commands
import discord
import asyncio
import traceback
import logging
import redis

loop = asyncio.get_event_loop()

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='SESTREN.log', encoding='utf-8', mode='a')
formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{")
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Instance started.")

prefix = ["$"]

initial_extensions = [
    "admin",
    "general",
    "vcaccess",
    "utils.help"
]

description = "Thane's bot for testing and building cogs."

try:
    with open('auth.json', 'r+') as auth_file:
        auth = json.load(auth_file)
        token = auth["prod"]
except FileNotFoundError:
    exit("auth.json not found in running directory.")

bot = commands.Bot(command_prefix=prefix, description=description, pm_help=False, self_bot=False)

try:
    with open('redis.json', 'r+') as redis_conf:
        conf = json.load(redis_conf)["db"]
        bot.db = redis.StrictRedis(**conf)
except FileNotFoundError:
    print('ERROR: redis.json not found in running directory')
    exit()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.message.channel.send(content='This command cannot be used in private messages.')

    elif isinstance(error, commands.DisabledCommand):
        await ctx.message.channel.send(content='This command is disabled and cannot be used.')

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.channel.send(content="You are missing required arguments.\n")

    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.channel.send(content="Command not found")

    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        traceback.print_tb(error.__traceback__, file=sys.stderr)
        log.error('In {0.command.qualified_name}:'.format(ctx))
        log.error('{0.__class__.__name__}: {0}'.format(error.original))

    else:
        traceback.print_tb(error.__traceback__, file=sys.stderr)


def owner(member: discord.Member):
    return member


@bot.event
async def on_guild_channel_update(before, after):
    print('on_guild_channel_update triggered')
    print(dir(after))


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(discord.utils.oauth_url(bot.user.id))
    # log.info("Initialized.")

    print('------')
    print(bot.owner_id)
    bot.owner = owner(bot.owner_id)


@bot.event
async def on_message(message):
    await bot.process_commands(message)


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
