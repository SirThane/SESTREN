"""
Module for listener for user's joining/leaving voice channels.

On join, adds role to grant access to voice channel.
On leave, removes access role.
"""

import discord
import json

class VCAccess:

    def __init__(self, bot):
        self.bot = bot

    @property
    def guild(self):
        return self.bot.get_guild(184502171117551617)

    @property
    def channel(self):
        return discord.Guild.get_channel(self.guild, 315232431835709441)

    @property
    def vc_guilds(self):
        pass

    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            await self.channel.send(content='Client {0.name} has changed voice state.\n\
            Previous channel: {1.channel}\nNew channel: {2.channel}'.format(member, before, after))
            print(member.guild.id)


def setup(bot):
    bot.add_cog(VCAccess(bot))
