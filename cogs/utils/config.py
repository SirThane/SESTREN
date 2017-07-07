import discord
from discord.ext import commands
from main import app_name
from cogs.utils import checks


config = f'{app_name}:config'


class Config:
    """For manual configuration of bot internals."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @checks.owner()
    @commands.group(name='redis', hidden=True)
    async def _redis(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Config(bot))
