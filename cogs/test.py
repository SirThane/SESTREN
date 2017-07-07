"""Should be obvious."""

import discord
from discord.ext import commands
from cogs.utils import utils, checks


class Test:

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

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
        # """T2 test subcommand  # Shhhh. We're testing the help formatter.
        #
        # [p]test t2 does even more nothing"""
        pass

    @checks.sudo()
    @commands.command(name='countdown', hidden=True)
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

    @commands.command(name='pagtest', hidden=True)
    async def pagtest(self, ctx):
        value = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.
Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.
Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"""
        pag = utils.paginate(value)
        em = discord.Embed(title='Pagination Test:', color=discord.Colour.green())
        c = 1
        for i in pag:
            em.add_field(name='Field {}'.format(c), value=i)
            c += 1
        await ctx.send(embed=em)

    @checks.sudo()
    @commands.command(name='redtest', disabled=True, hidden=True)
    async def redtest(self, ctx, *, message: str):
        '''Test docstr'''
        self.db.hset('redtest', ctx.message.id, message)

def setup(bot):
    bot.add_cog(Test(bot))