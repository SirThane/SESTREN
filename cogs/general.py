# -*- coding: utf-8 -*-

"""General Commands"""


# Lib
from datetime import datetime

# Site
from discord.colour import Colour
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command
from discord.member import Member
from discord.utils import find

# Local
from utils.checks import sudo
from utils.classes import Bot, Embed, SubRedis


class General(Cog):
    """General use and utility commands."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = SubRedis(bot.db, "general")

        self.errorlog = bot.errorlog

    @command(name='userinfo', no_private=True)
    async def userinfo(self, ctx: Context, member: Member = None):
        """Gets current server information for a given user

         [p]userinfo @user
         [p]userinfo username#discrim
         [p]userinfo userid"""

        if member is None:
            member = ctx.message.author

        roles = str([r.name for r in member.roles if '@everyone' not in r.name]).strip('[]').replace(', ', '\n').replace("'", '')
        if roles == '':
            roles = 'User has no assigned roles.'

        emb = {
            'embed': {
                'title': 'User Information For:',
                'description': f'{member.name}#{member.discriminator}',
                'color': getattr(Colour, member.default_avatar.name)()
            },
            'author': {
                'name': '{0.name} || #{1.name}'.format(ctx.guild, ctx.channel),
                'icon_url': ctx.guild.icon_url
            },
            'fields': [
                {
                    'name': 'User ID',
                    'value': str(member.id),
                    'inline': True
                },
                {
                    'name': 'Display Name:',
                    'value': member.display_name if not member.name else '(no display name set)',
                    'inline': True
                },
                {
                    'name': 'Roles:',
                    'value': roles,
                    'inline': False
                },
                {
                    'name': 'Account Created:',
                    'value': member.created_at.strftime("%b. %d, %Y\n%I:%M %p"),  # ("%Y-%m-%d %H:%M"),
                    'inline': True
                },
                {
                    'name': 'Joined Server:',
                    'value': member.joined_at.strftime("%b. %d, %Y\n%I:%M %p"),
                    'inline': True
                },
            ],
            'footer': {
                'text': 'Invoked by {0.name}#{0.discriminator} || {1}\
                        '.format(ctx.message.author, datetime.utcnow().strftime("%b. %d, %Y %I:%M %p")),
                'icon_url': ctx.message.author.avatar_url
            }
        }

        embed = Embed(**emb['embed'])  # TODO: EMBED FUNCTION/CLASS
        embed.set_author(**emb['author'])
        embed.set_thumbnail(url=member.avatar_url_as(format='png'))
        for field in emb['fields']:
            embed.add_field(**field)
        embed.set_footer(**emb['footer'])

        await ctx.channel.send(embed=embed)

    @command(name='ping')
    async def ping(self, ctx: Context):
        """Your basic `ping`"""

        await ctx.send('pong')

    @sudo()
    @command(name='discrim')
    async def discrim(self, ctx: Context, *, member: Member = None):
        """Finds a username that you can use to change discriminator

        [p]discrim"""

        if not member:
            member = ctx.author

        d = member.discriminator
        f = find(lambda x: x.discriminator == d and not x.id == member.id, self.bot.get_all_members())

        if f is not None:
            em = Embed(
                title="Discrim",
                description=f"Change your name to `{f.name}` and then back "
                            f"to `{member.name}` to get a new discriminator",
                colour=0x00FF00)

        else:
            em = Embed(
                title="Sorry",
                description="I couldn't find another person with your discriminator",
                colour=0xFF0000
            )

        await ctx.send(embed=em)

    @command(name='learnpy')
    async def learnpy(self, ctx: Context):
        """Links some tutorials for Python"""

        msg = """
Well, I started here and everyone said I shouldn't bother with it because it has an old Python version, but for someone who's not just new to Python, but new to programming in general, use https://codecademy.com/.
It's very interactive, and even though you can't really do anything with what you learn, it will familiarize you with the fundamentals.
It's free. There are some other resources that you can use afterwards, but I would suggest starting here.
http://python.swaroopch.com/ (for complete beginners to programming)
https://learnxinyminutes.com/docs/python3/ (for people who know programming already)
https://docs.python.org/3.5/tutorial/ (for the in-between group, i.e. knows some programming but not a lot)
see also: http://www.codeabbey.com/ (exercises for beginners)
http://www.learnpython.org/ (somewhat interactive tutorial)
Also, this guy's video tutorials are excellent.
https://www.youtube.com/playlist?list=PL-osiE80TeTskrapNbzXhwoFUiLCjGgY7
https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU
https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc
"""
        await ctx.send(msg)


def setup(bot):
    """General"""
    bot.add_cog(General(bot))
