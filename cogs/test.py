"""Should be obvious."""

import discord
from discord.ext import commands


class Test:
    """Test commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='test')
    async def test(self, ctx, *, arg):
        """Test group

        [p]test does nothing"""
        pass

    @test.command(name='t1')
    async def t1(self, ctx, *, arg):
        """T1 test subcommand

        [p]test t1 also does nothing"""
        pass

    @test.command(name='t2')
    async def t2(self, ctx, *, arg):
        """T2 test subcommand

        [p]test t2 does even more nothing"""
        pass


def setup(bot):
    bot.add_cog(Test(bot))