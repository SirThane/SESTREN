"""
Currently a test bot.
"""

import json
import sys
from discord.ext import commands
import discord
import asyncio
import traceback
import logging

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

description = "Personal bot for Thane"

try:
    with open('auth.json', 'r+') as auth_file:
        auth = json.load(auth_file)
        token = auth["prod"]
except IOError:
    sys.exit("auth.json not found in running directory.")

bot = commands.Bot(command_prefix=prefix, description=description, pm_help=False, self_bot=False)

@bot.event
async def on_command_error(ctx, error):
    await bot.formatter.format_help_for(ctx, ctx.command if not None else bot)
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
        traceback.print_tb(error.original.__traceback__, file=sys.stderr)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(discord.utils.oauth_url(bot.user.id))
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
