"""Should be obvious."""

# Lib
from asyncio import sleep
from typing import Any

# Site
from discord.ext.commands.cog import Cog
from discord.colour import Colour
from discord.ext.commands.context import Context
from discord.ext.commands.core import group, command

# Local
from utils.checks import sudo
from utils.classes import Bot, Embed, Paginator, SubRedis


class Test(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = SubRedis(bot.db, "test")

        self.errorlog = bot.errorlog

    @group(name='test')
    async def test(self, ctx: Context, *, arg: Any):
        pass

    @test.group(name='t1')
    async def t1(self, ctx: Context, *, arg: Any):
        """Test"""
        pass

    @t1.command(name='t1_1')
    async def t1_1(self, ctx: Context, *, arg: Any):
        """T1 subcommand"""
        pass

    @test.command(name='t2')
    async def t2(self, ctx: Context):
        """Supposed to print shit"""
        print(dir(ctx))
        print()
        print(dir(ctx.command))

    @sudo()
    @command(name='countdown')
    async def countdown(self, ctx: Context, seconds: int):
        """Counts down from <seconds>

        [p]countdown <number of seconds>"""
        if seconds > 600:
            await ctx.send("{}, I cannot count down for anytime longer than 600 seconds".format(ctx.author.mention))
            return

        else:
            em = Embed(title="countown", description=str(seconds))
            count = await ctx.send(embed=em)
            await sleep(1)
            for i in list(range(seconds))[::-1]:
                em = Embed(title="countdown", description=i)
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

    @command(name='pagtest')
    async def pagtest(self, ctx: Context, value: str = None):
        if not value:
            value = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.
Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.
Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.
Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur?
Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"""
        pag = Paginator(1024).paginate(value)
        em = Embed(title='Pagination Test:', color=Colour.green())
        for i in range(len(pag)):
            em.add_field(name='Field {}'.format(i), value=pag[i])
        await ctx.send(embed=em)

    @sudo()
    @command(name='redtest')
    async def redtest(self, ctx: Context, *, message: str):
        """Test docstr"""
        self.config.hset('redtest', ctx.message.id, message)

    @sudo()
    @command(name="embtest")
    async def embtest(self, ctx: Context):
        d = {
              "content": "this `supports` __a__ **subset** *of* ~~markdown~~ 😃 ```js\nfunction foo(bar) {\n  console.log(bar);\n}\n\nfoo(1);```",
              "embed": {
                "title": "title ~~(did you know you can have markdown here too?)~~",
                "description": "this supports [named links](https://discordapp.com) on top of the previously shown subset of markdown. ```\nyes, even code blocks```",
                "url": "https://discordapp.com",
                "color": 4830089,
                "footer": {
                  "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png",
                  "text": "footer text"
                },
                "thumbnail": {
                  "url": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                "image": {
                  "url": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                "author": {
                  "name": "author name",
                  "url": "https://discordapp.com",
                  "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
                },
                "fields": [
                  {
                    "name": "🤔",
                    "value": "some of these properties have certain limits..."
                  },
                  {
                    "name": "😱",
                    "value": "try exceeding some of them!"
                  },
                  {
                    "name": "🙄",
                    "value": "an informative error should show up, and this view will remain as-is until all issues are fixed"
                  },
                  {
                    "name": "<:thonkang:219069250692841473>",
                    "value": "these last two",
                    "inline": True
                  },
                  {
                    "name": "<:thonkang:219069250692841473>",
                    "value": "are inline fields",
                    "inline": True
                  }
                ]
              }
            }
        em = Embed.from_dict(d['embed'])
        await ctx.send(d['content'], embed=em)

    @command()
    async def c4test(self, ctx: Context):
        await ctx.send(embed=Embed(description=":one::two::three::four::five::six::seven:"))


def setup(bot: Bot):
    """Test"""
    bot.add_cog(Test(bot))
