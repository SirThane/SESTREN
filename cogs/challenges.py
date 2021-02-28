# -*- coding: utf-8 -*-

# Lib
from asyncio import sleep
from random import choice

# Site
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command

# Local
from utils.classes import Bot, Embed, SubRedis
from utils.checks import sudo


class Challenges(Cog):
    """Challenge entries for Python! Discord https://discord.gg/8NWhsvT"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = SubRedis(bot.db, "challenges")

    def loading(self, ctx: Context, title: str, color: int, sec: int, inter: int) -> None:
        em = Embed(title=title, description='', color=color)

    @command(name="SerialGen")
    async def SerialGen(self, ctx: Context, *, template: str):
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

        UPPER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        LOWER = list(map(lambda x: x.lower(), UPPER))
        ALPHA = UPPER + LOWER
        NUMERAL = [n for n in range(10)]
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

        em = Embed(
            title='SerialGen: Generating Serial. . .',
            description='Please wait.',
            color=ctx.guild.me.color
        )
        em.set_author(
            name=f'{ctx.author.name}#{ctx.author.discriminator}',
            icon_url=ctx.author.avatar_url_as(format='png')
        )

        msg = await ctx.send(embed=em)

        for n in range(1, seconds + 1):
            await sleep(1)
            em = Embed(
                title='SerialGen: Generating Serial. . .',
                description=f'Progress: {int(100 / seconds) * n}%',
                color=ctx.guild.me.color
            )
            em.set_author(
                name=f'{ctx.author.name}#{ctx.author.discriminator}',
                icon_url=ctx.author.avatar_url_as(format='png')
            )
            await msg.edit(embed=em)

        else:
            await sleep(1)
            em = Embed(
                title='SerialGen: Complete!',
                description='Progress: 100%',
                color=ctx.guild.me.color
            )
            em.set_author(
                name=f'{ctx.author.name}#{ctx.author.discriminator}',
                icon_url=ctx.author.avatar_url_as(format='png')
            )
            em.add_field(
                name='Serial has been created:',
                value=f'```{ret}```'
            )
            await msg.edit(embed=em)


def setup(bot: Bot):
    """Challenges"""
    bot.add_cog(Challenges(bot))
