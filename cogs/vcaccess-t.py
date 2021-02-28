"""
Module for listener for user's joining/leaving voice channels.

On join, adds role to grant access to voice channel.
On leave, removes access role.
"""


import discord
from discord.ext import commands
from utils import checks


class VCAccess:
    """Module for listener for user's joining/leaving voice channels.

    On join, adds role to grant access to voice channel.
    On leave, removes access role."""
    def __init__(self, bot):
        self.bot = bot
        # self._data = config.Config("vc_access.json")
        self.db = bot.config

    # @property  # I'D STARTED WORKING ON THIS WHEN I WAS SHOWN DANNY'S CONFIG.PY AND I DON'T WANT TO THROW IT AWAY
    # def _data(self):
    #     """Load JSON config to property 'data'
    #
    #     Format:
    #     {
    #         "<guild id>": {
    #             "<voice channel id>": "<role id>"
    #         }
    #     }"""
    #     try:
    #         with open('vc_access.json', 'r+') as datafile:
    #             return json.load(datafile)
    #     except IOError:
    #         print("vc_access.json not found.")
    #         self.bot.unload_extension('cogs.utils.vc_access')

    @property
    def guilds(self):
        return list(self.db.smembers('vca:guilds'))

    def channels(self, g):
        for c in self.db.hkeys(f'vca:guilds:{g}'):  # self._data.get(g):
            yield c

    async def modifyrole(self, member, voicestate, add=True):
        guild = str(voicestate.channel.guild.id)
        if guild in self.guilds:
            channel = str(voicestate.channel.id)
            if channel in self.channels:
                channels = self._data.get(guild)
                if channel in channels:
                    role = discord.utils.get(voicestate.channel.guild.roles, id=int(channels[channel]))
                    if add:
                        await member.add_roles(role)
                    else:
                        await member.remove_roles(role)
                        try:
                            member.roles.remove(role)
                        except IndexError:
                            pass
                        except ValueError:
                            pass

    @checks.sudo()
    @commands.group(name='vca')
    async def vca(self, ctx):
        """Voice Channel Access Control

        [p]vca (subcommand)"""
        pass

    @vca.command(name='list')
    async def _list(self, ctx):
        """Lists channels VCA is active on for current server."""
        g = str(ctx.guild.id)
        if g not in self.guilds:
            await ctx.send(embed=discord.Embed(title=f'VCA not currently enabled on {ctx.guild.name}',
                                               color=ctx.guild.me.color))
        else:
            field = ''
            for c in self.channels(g):
                channel = discord.utils.get(ctx.guild.channels, id=int(c))
                role = discord.utils.get(ctx.guild.roles, id=int(self.db.hget(f'vca:guilds:{g}', c)))
                field += '{0.name}: {1.name}\n'.format(channel, role)
            embed = discord.Embed(color=ctx.guild.me.color)
            embed.add_field(name=f'VCA active in {ctx.guild.name} on the following channels:', value=field)
            await ctx.send(embed=embed)

    @checks.sudo()
    @vca.command(name='addchannel', aliases=['add'])
    async def addchannel(self, ctx, channel: str, role: str):
        """Adds a Voice Channel to VCA

        [p]vca chan add (voice channel id) (role id)"""
        color = ctx.guild.me.color
        c = discord.utils.get(ctx.guild.channels, id=int(channel))
        r = discord.utils.get(ctx.guild.roles, id=int(channel))
        if c is not None and r is not None:
            if channel in self.channels(ctx.guild.id):
                em = discord.Embed(title='Error Adding Channel/Role Pair:',
                                   description=f'{c.name} already associated with {r.name}\n'
                                               f'Please dissociate {c.name} by using'
                                               f'`{self.bot.formatter.clean_prefix}vca removechannel` first.',
                                   color=color)
                await ctx.send(embed=em)
            else:
                if str(ctx.guild.id) not in self.guilds:
                    self.db.sadd('vca:guilds', ctx.guild.id)
                try:
                    self.db.hset(f'vca:guilds:{ctx.guild.id}', channel, role)
                    em = discord.Embed(title='Success',
                                       description=f'VCA now active for {c.name}', color=color)
                    await ctx.send(embed=em)
                except Exception as e:
                    em = discord.Embed(title='Error',
                                       description='An error prevented the operation from completing.',
                                       color=color)
                    em.add_field(name='Error Details:', value=f'**{type(e).__name__}**: {e}')
                    em.set_footer(text='Please report this error to the developer, {0}'.format(self.bot.owner))
                    await ctx.send(embed=em)
        else:
            em = discord.Embed(title='Error',
                               description='Channel or Role not found in current guild.',
                               color=color)
            await ctx.send(embed=em)

    @checks.sudo()
    @vca.command(name='removechannel', aliases=['rem'])
    async def _removechannel(self, ctx, channel: str):
        """Removes a Voice Channel from VCA

        [p]vca chan remove (voice channel id)"""
        if channel in self.channels:
            for guild in self.guilds:
                d = self._data.get(guild)
                if channel in list(d):
                    g = discord.utils.get(self.bot.guilds, id=int(guild))
                    c = discord.utils.get(g.voice_channels, id=int(channel))
                    del d[channel]
                    await self._data.put(guild, d)
                    await ctx.message.channel.send(content='`{0}` has been removed from VCA.'.format(c))
        else:
            ctx.message.channel.send(content='Cannot find channel id `{0}` in VCA.'.format(channel))

    async def on_voice_state_update(self, member, before, after):
        b, a = before.channel, after.channel
        if a is not None and b is None:
            await self.modifyrole(member, after)
        elif a is None and b is not None:
            await self.modifyrole(member, before, False)
        elif a is not None and b is not None:
            await self.modifyrole(member, before, False)
            await self.modifyrole(member, after)


def setup(bot):
    bot.add_cog(VCAccess(bot))
