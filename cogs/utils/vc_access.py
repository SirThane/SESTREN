"""
Module for listener for user's joining/leaving voice channels.

On join, adds role to grant access to voice channel.
On leave, removes access role.
"""

import discord
from discord.ext import commands
import json

class VCAccess:

    def __init__(self, bot):
        self.bot = bot

    @property
    def data(self):
        try:
            with open('vc_access.json', 'r+') as datafile:
                return json.load(datafile)
        except IOError:
            print("vc_access.json not found.")
            self.bot.unload_extension('cogs.utils.vc_access')

    @property
    def servers(self):
        return self.data.keys()


    @property
    def guild(self):
        return self.bot.get_guild(184502171117551617)

    @property
    def channel(self):
        return discord.Guild.get_channel(self.guild, 315232431835709441)


    @commands.group()
    async def vca(self):
        """Voice Channel Access command group

        Help docstr here later
        [p]vca addguild <guild id>
        [p]vca removeguild <guild id>"""
        pass

    @vca.command(name='add')
    async def addguild(self, ctx, guild: int):
        pass

    @vca.command(name='rem')
    async def removeguild(self, ctx, guild: int):
        pass


    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            await self.channel.send(content='Client {0.name} has changed voice state.\n\
            Previous channel: {1.channel}\nNew channel: {2.channel}'.format(member, before, after))


def setup(bot):
    bot.add_cog(VCAccess(bot))
