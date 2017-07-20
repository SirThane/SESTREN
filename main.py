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
from cogs.utils import utils


loop = asyncio.get_event_loop()

app_name = 'SESTREN'  # BOT NAME HERE

try:
    with open('redis.json', 'r+') as redis_conf:
        conf = json.load(redis_conf)["db"]
except FileNotFoundError:
    print('ERROR: redis.json not found in running directory')
    exit()
except:
    print('ERROR: could not load configuration')
    exit()

log = logging.getLogger()
log.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=f'{app_name}.log', encoding='utf-8', mode='a')
formatter = logging.Formatter("{asctime} - {levelname} - {message}", style="{")
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Instance started.")

db = utils.StrictRedis(**conf)
config = f'{app_name}:config'
bot = commands.Bot(command_prefix=db.lrange(f'{config}:prefix', 0, -1), **db.hgetall(f'{config}:instance'))
bot.db = db


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(content='This command cannot be used in private messages.')

    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(content='This command is disabled and cannot be used.')

    elif isinstance(error, commands.MissingRequiredArgument):
        await bot.formatter.format_help_for(ctx, ctx.command, "You are missing required arguments.")

    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found. (I\'m working on fixing cmd_not_found forf help module')
        # await bot.formatter.format_help_for(ctx, [c for c in bot.commands if 'help' == c.name][0],
        #                                     "Command not found.")

    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
        traceback.print_tb(error.__traceback__, file=sys.stderr)
        log.error('In {0.command.qualified_name}:'.format(ctx))
        log.error('{0.__class__.__name__}: {0}'.format(error.original))

    else:
        traceback.print_tb(error.__traceback__, file=sys.stderr)


@bot.event
async def on_ready():
    app_info = await bot.application_info()
    bot.owner = discord.utils.get(bot.get_all_members(), id=app_info.owner.id)
    await bot.change_presence(game=discord.Game(name=f'{bot.command_prefix[0]}help'))

    print(f'#-------------------------------#\n'
          f'| Successfully logged in.\n'
          f'#-------------------------------#\n'
          f'| Username:  {bot.user.name}\n'
          f'| User ID:   {bot.user.id}\n'
          f'| Owner:     {bot.owner}\n'
          f'| Guilds:    {len(bot.guilds)}\n'
          f'| Users:     {len(list(bot.get_all_members()))}\n'
          f'| OAuth URL: {discord.utils.oauth_url(bot.user.id)}\n'
          f'# ------------------------------#')


@bot.event
async def on_message(message):
    await bot.process_commands(message)


if __name__ == "__main__":
    print(f'\n'
          f'#-------------------------------#')

    for cog in db.lrange(f'{config}:initial_cogs', 0, -1):
        try:
            print(f'| Loading initial cog {cog}')
            bot.load_extension(f'cogs.{cog}')
            log.info(f'Loaded {cog}')
        except Exception as e:
            log.warning('Failed to load extension {}\n{}: {}'.format(cog, type(e).__name__, e))
            print('| Failed to load extension {}\n|   {}: {}'.format(cog, type(e).__name__, e))

    print(f'#-------------------------------#\n')
    run = {
        'token': db.hget(f'{config}:run', 'token'),
        'bot': db.hget(f'{config}:run', 'bot')
    }
    bot.run(run['token'], bot=run['bot'])
