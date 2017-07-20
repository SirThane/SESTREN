import discord
from discord.ext import commands


class Challenges:
    """Challenge entries for Python! Discord https://discord.gg/8NWhsvT"""
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    def loading(self, ctx, title, color, sec, inter):
        em = discord.Embed(title=title, description='', color=color)

    @commands.command(name="SerialGen")
    async def SerialGen(self, ctx, *, template: str):
        """Generates a fake serial based on a template.

        Date: 7/10/2017
        ```
        Title = "SerialGen"
        Difficulty = "A script kiddie can do it."
        Theme = "Application (Generation) Tool"

        That is just simple. It will generate some serial keys, using an input template... Example:

        input: ###-###-12-^^^
        LOL-XDD-12-007 < random serial key
        input: @@@@@-@@@@@
        aBcDe-VwXyZ < random serial key
        input: #@@^^
        XMn12 < random serial key
        input: &&&-###
        1A2-WOW < random serial key

        This challenge is fun! You don't need good luck to make it.```

        **__Key:__**
        ```
        ^ : Uppercase character
        @ : Lowercase character
        $ : Any alpha character
        # : Numeral character
        & : Any alphanumeric character (Uppercase)
        % : Any alphanumeric character (Lowercase)
        ? : Any alphanumeric character
        ```"""
        from random import choice
        from asyncio import sleep
        UPPER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        LOWER = list(map(lambda x: x.lower(), UPPER))
        ALPHA = UPPER + LOWER
        NUMERAL = [n for n in range(1, 11)]
        AN_UPPER = UPPER + NUMERAL
        AN_LOWER = LOWER + NUMERAL
        ANY = ALPHA + NUMERAL

        ret = ''

        for char in template:
            if char == '^':
                ret = f'{ret}{choice(UPPER)}'
            elif char == '@':
                ret = f'{ret}{choice(LOWER)}'
            elif char == '$':
                ret = f'{ret}{choice(ALPHA)}'
            elif char == '#':
                ret = f'{ret}{choice(NUMERAL)}'
            elif char == '&':
                ret = f'{ret}{choice(AN_UPPER)}'
            elif char == '%':
                ret = f'{ret}{choice(AN_LOWER)}'
            elif char == '?':
                ret = f'{ret}{choice(ANY)}'
            else:
                ret = f'{ret}{char}'

        seconds = int(len(ret) / 5)

        em = discord.Embed(title='SerialGen: Generating Serial. . .',
                           description='Please wait.',
                           color=ctx.guild.me.color)
        em.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}',
                      icon_url=ctx.author.avatar_url_as(format='png'))

        msg = await ctx.send(embed=em)

        for n in range(1, seconds + 1):
            await sleep(1)
            em = discord.Embed(title='SerialGen: Generating Serial. . .',
                               description=f'Progress: {int(100 / seconds) * n}%',
                               color=ctx.guild.me.color)
            em.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}',
                          icon_url=ctx.author.avatar_url_as(format='png'))
            await msg.edit(embed=em)
        else:
            await sleep(1)
            em = discord.Embed(title='SerialGen: Complete!',
                               description='Progress: 100%',
                               color=ctx.guild.me.color)
            em.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}',
                          icon_url=ctx.author.avatar_url_as(format='png'))
            em.add_field(name='Serial has been created:', value=f'```{ret}```')
            await msg.edit(embed=em)


def setup(bot):
    bot.add_cog(Challenges(bot))
