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

    @commands.command(name='countdown')
    async def countdown(self, ctx, seconds: int):
        """Counts down from <seconds>

        [p]countdown <number of seconds>"""
        from asyncio import sleep
        if seconds > 600:
            await ctx.send("{}, I cannot count down for anytime longer than 600 seconds".format(ctx.messsage.author.mention))
            return
        else:
            em = discord.Embed(title="countown", description=str(seconds))
            count = await ctx.send(embed=em)
            sleep(1)
            for i in list(range(seconds))[::-1]:
                em = discord.Embed(title="countdown", description=i)
                await count.edit(embed=em)
                await sleep(1)
            await count.delete()

        # import math
        # def _hex(r: int, g: int, b: int):
        #     return (r * 0x10000) + (g * 0x100) + (b)
        #
        # c = [0, 255, 0]
        # h = _hex(*c)
        # s = 10
        # sr = math.floor((255 / s))
        # for i in range(10):
        #     global c
        #     c = [c[0] + sr, c[1] - sr, 0]
        #     h = _hex(*c)
        #     print(hex(h))


def setup(bot):
    bot.add_cog(Test(bot))