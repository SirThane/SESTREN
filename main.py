# -*- coding: utf-8 -*-

"""SESTREN"""

# Lib
from json import load
from typing import List

# Site
from discord.activity import Activity
from discord.channel import TextChannel
from discord.ext.commands import when_mentioned
from discord.flags import Intents
from discord.message import Message
from discord.utils import oauth_url

# Local
from utils.classes import Bot, ErrorLog, Redis, SubRedis


APP_NAME = "SESTREN"  # BOT NAME HERE


"""
Minimum Redis Schema

:namespace {APP_NAME}:config:
    :HASH {APP_NAME}:config:instance
        :key description:       str         # Description will be used for Help
        :key dm_help:           bool        # If Help output will be forced to DMs
        :key errorlog:          int         # Channel ID for errorlog channel
    :HASH {APP_NAME}:config:run
        :key bot:               bool        # If bot account
        :key token:             str         # Login token
    :HASH {APP_NAME}:config:prefix:config
        :key default_prefix:    str         # Default bot prefix
        :key when_mentioned:    bool        # Whether bot mentions count as prefix


Redis Configuration JSON Schema

:file ./redis.json
{
  "host": "localhost",                      # Server address hosting Redis DB
  "port": 6379,                             # Port for accessing Redis
  "db": 0,                                  # Redis DB number storing app configs
  "decode_responses": true                  # decode_responses must be bool true
}
"""


try:
    with open("redis.json", "r+") as redis_conf:
        conf = load(redis_conf)
        db = SubRedis(Redis(**conf), APP_NAME)
        config = SubRedis(db, "config")

except FileNotFoundError:
    raise FileNotFoundError("redis.json not found in running directory")


if not config.hget("instance", "description"):
    config.hset("instance", "description", "")

if not config.hget("instance", "dm_help"):
    config.hset("instance", "dm_help", "True")

if not config.hget("prefix:config", "default_prefix"):
    config.hset("prefix:config", "default_prefix", "!")

if not config.hget("prefix:config", "when_mentioned"):
    config.hset("prefix:config", "when_mentioned", "False")


def command_prefix(client: Bot, msg: Message) -> List[str]:
    """Callable to determine guild-specific prefix or default"""

    # Get default prefix and whether mentions count
    prefix_config = config.hgetall("prefix:config")

    prefix = [prefix_config["default_prefix"]]
    if prefix_config["when_mentioned"]:
        prefix.extend(when_mentioned(client, msg))

    # If in a guild, check for guild-specific prefix
    if isinstance(msg.channel, TextChannel):
        guild_prefix = config.hget("prefix:guild", msg.channel.guild.id)
        if guild_prefix:
            prefix.append(guild_prefix)

    return prefix


intents = Intents.all()


bot = Bot(db=db, app_name=APP_NAME, command_prefix=command_prefix, intents=intents, **config.hgetall("instance"))


@bot.event
async def on_ready():
    """Coroutine called when bot is logged in and ready to receive commands"""

    # "Loading" status message
    loading = "around, setting up shop."
    await bot.change_presence(activity=Activity(name=loading, type=0))

    # Bot account metadata such as bot user ID and owner identity
    bot.app_info = await bot.application_info()
    bot.owner = bot.get_user(bot.app_info.owner.id)

    # Add the ErrorLog object if the channel is specified
    if bot.errorlog_channel:
        bot.errorlog = ErrorLog(bot, bot.errorlog_channel)

    print(f"\n#-------------------------------#")

    # Load all initial cog names stored in db
    for cog in config.lrange("initial_cogs", 0, -1):
        try:
            print(f"| Loading initial cog {cog}")
            bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            print(f"| Failed to load extension {cog}\n|   {type(e).__name__}: {e}")

    # "Ready" status message
    ready = f"{config.hget('prefix:config', 'default_prefix')}help for help"
    await bot.change_presence(activity=Activity(name=ready, type=2))

    # Pretty printing ready message and general stats
    print(f"#-------------------------------#\n"
          f"| Successfully logged in.\n"
          f"#-------------------------------#\n"
          f"| Username:  {bot.user.name}\n"
          f"| User ID:   {bot.user.id}\n"
          f"| Owner:     {bot.owner}\n"
          f"| Guilds:    {len(bot.guilds)}\n"
          f"| Users:     {len(list(bot.get_all_members()))}\n"
          f"| OAuth URL: {oauth_url(bot.app_info.id)}\n"
          f"# ------------------------------#")


@bot.event
async def on_message(msg: Message):
    await bot.process_commands(msg)


if __name__ == "__main__":
    bot.run(**config.hgetall("run"))
