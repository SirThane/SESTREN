"""
Module for listener for user's joining/leaving voice channels.

On join, adds role to grant access to voice channel.
On leave, removes access role.
"""


import discord
from discord.ext import commands
# import json
from cogs.utils import danny_config


class VCAccess:
    """Module for listener for user's joining/leaving voice channels.

    On join, adds role to grant access to voice channel.
    On leave, removes access role."""
    def __init__(self, bot):
        self.bot = bot
        self._data = danny_config.Config("cogs/vc_access.json")

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
        return list(self._data)

    @property
    def channels(self):
        l = []
        for g in self.guilds:
            for c in self._data.get(g):
                l.append(c)
        return l

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

    @commands.group(name='vca')
    async def vca(self, ctx):
        """Voice Channel Access Control

        [p]vca addguild (guild id)
        [p]vca removeguild (guild id)
        [p]vca chan (subcommand)"""
        pass

    @vca.command(name='addguild', aliases=['add'])
    async def addguild(self, ctx, gid: int):  # g = discord.Guild.id
        """Activates VCA on a guild

        [p]vca addguild (guild id)"""
        gstr = str(gid)
        gobj = discord.utils.get(self.bot.guilds, id=gid)
        if gobj is not None:
            if gstr in self.guilds:
                await ctx.message.channel.send(content='VCA already active on {0.name}.'.format(gobj))
            else:
                await self._data.put(gid, {})
                await ctx.message.channel.send(content='VCA now active on {0.name}'.format(gobj))
        else:
            await ctx.message.channel.send(content='Server id {0} not found. Make sure SESTREN is a member.'.format(gid))

    @vca.command(name='removeguild', aliases=['rem'])
    async def removeguild(self, ctx, gid: int):
        """Deactivates VCA on a guild.

        This will remove all channels from VCA belonging
        to the guild.

        [p]vca removeguild (guild id)"""
        gstr = str(gid)
        gobj = discord.utils.get(self.bot.guilds, id=gid)
        if gobj is not None:
            if gstr in self.guilds:
                await self._data.remove(gstr)
                await ctx.message.channel.send(content='{0.name} removed from VCA.'.format(gobj))
            else:
                await ctx.message.channel.send(content='VCA is not active on {0.name}'.format(gobj))
        else:
            await ctx.message.channel.send(content='Server id {0} not found. Make sure SESTREN is a member.'.format(gid))

    @vca.command(name='list')
    async def _list(self, ctx, *args):
        """Lists servers and channels VCA is active on.

        ."""
        out = '```\nVoice Channel Access control active on the following servers:\n{0}\n'.format('-'*61)
        for g in self.guilds:
            guild = discord.utils.get(self.bot.guilds, id=int(g))
            out += '{0}\n'.format(guild.name)
            channels = self._data.get(g)
            if not len(channels) == 0:
                for c in channels:
                    channel = discord.utils.get(guild.channels, id=int(c))
                    role = discord.utils.get(guild.roles, id=int(channels[c]))
                    out += '--- {0} : {1}\n'.format(channel.name, role.name)
        else:
            out += '```'
        await ctx.message.channel.send(content=out)


    @vca.group(name='chan')
    async def chan(self, ctx):
        """Voice Channel Access `role` command group

        [p]vca chan add (voice channel id) (role id)
        [p]vca chan rem (voice channel id)"""
        pass

    @chan.command(name='addchannel', aliases=['add'])
    async def addchannel(self, ctx, guild: str, channel: str, role: str):
        """Adds a Voice Channel to VCA

        [p]vca chan add (voice channel id) (role id)"""
        g = discord.utils.get(self.bot.guilds, id=int(guild))
        c = discord.utils.get(g.voice_channels, id=int(channel))
        r = discord.utils.get(g.roles, id=int(role))
        if g is not None and c is not None and r is not None:
            if guild not in self.guilds:
                await self._data.put(guild, {})
                await ctx.message.channel.send(content='VCA is now active on `{0}`'.format(g))
            d = self._data.get(guild)
            d[channel] = role
            await self._data.put(guild, d)
            await ctx.message.channel.send(content='VCA is now active on channel `{0}` for role `{1}`'.format(c, r))

    @chan.command(name='removechannel', aliases=['rem'])
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
