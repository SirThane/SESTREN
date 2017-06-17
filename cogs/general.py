"""General Commands"""

import discord
from discord.ext import commands


class General:
    """General use and utility commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='userinfo', no_private=True)
    async def userinfo(self, ctx, member: discord.Member=None):
        """Gets current server information for a given user

         [p]userinfo @user
         [p]userinfo username#discrim
         [p]userinfo userid"""

        from datetime import datetime

        if member is None:
            member = ctx.message.author

        roles = str([r.name for r in member.roles if '@everyone' not in r.name]).strip('[]').replace(', ', '\n').replace("'", '')
        if roles == '':
            roles = 'User has no assigned roles.'

        emb = {
            'embed': {
                'title': 'User Information For:',
                'description': '{0.name}#{0.discriminator}'.format(member),
                'color': getattr(discord.Colour, member.default_avatar.name)()
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
                    'value': member.display_name if not None else '(no display name set)',
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

        embed = discord.Embed(**emb['embed'])  # TODO: EMBED FUNCTION/CLASS
        embed.set_author(**emb['author'])
        embed.set_thumbnail(url=member.avatar_url_as(format='gif'))
        for field in emb['fields']:
            embed.add_field(**field)
        embed.set_footer(**emb['footer'])

        await ctx.channel.send(embed=embed)

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Your basic `ping`"""
        await ctx.send('pong')

    @commands.command(name='discrim')
    async def discrim(self, ctx, *, member: discord.Member=None):
        """Finds a username that you can use to change discriminator

        [p]discrim"""
        if not member:
            member = ctx.author

        d = member.discriminator
        f = discord.utils.find(lambda x: x.discriminator == d and not x.id == member.id,
                               self.bot.get_all_members())
        if f is not None:
            em = discord.Embed(title="Discrim",
                               description="Change your name to `{}` and then back to `{}` to get a new discriminator"
                                           "".format(f.name, member.name), colour=0x00FF00)
            await ctx.send(embed=em)
        else:
            em = discord.Embed(title="Sorry",
                               description="I couldn't find another person with your discriminator", colour=0xFF0000)
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(General(bot))
