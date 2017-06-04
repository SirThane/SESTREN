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
        """Load JSON config to property 'data'

        Format:
        {
            "<guild id>": {
                "<voice channel id>": "<role id>"
            }
        }"""
        try:
            with open('vc_access.json', 'r+') as datafile:
                return json.load(datafile)
        except IOError:
            print("vc_access.json not found.")
            self.bot.unload_extension('cogs.utils.vc_access')

    @property
    def guilds(self):
        return self.data.keys()

    @staticmethod
    def channels(self, guild):
        guildid = str(guild.id)
        return data[guildid].keys()

    def update(self): ### WRITE FUNCTION TO OPEN JSON IN WRITE MODE FOR UPDATING
        pass


    @property ### PERSONAL GARBAGE EXPLICIT DEFINITIONS FOR FUNCTION TESTING
    def selfguild(self):
        return self.bot.get_guild(184502171117551617)

    @property
    def selfchannel(self):
        return discord.Guild.get_channel(self.selfguild, 315232431835709441)

    @commands.command(name='test')
    async def _test


    @commands.group()
    async def vca(self):
        """Voice Channel Access command group

        Help docstr here later
        [p]vca addguild <guild id>
        [p]vca removeguild <guild id>
        [p]vca role <subcommand>"""
        pass

    @vca.command(name='add')
    async def addguild(self, ctx, guild: int):
        pass

    @vca.command(name='rem')
    async def removeguild(self, ctx, guild: int):
        pass

    @vca.group()
    async def role(self):
        """Voice Channel Access subcommand `role` command group

        [p]vca role add <guild id> <voice channel id> <role id>
        [p]vca role rem <guild id> <voice channel id>"""
        pass

    @role.command(name='add')
    async def addrole(self, ctx, role: int):
        pass

    @role.command(name='rem')
    async def removerole(self, ctx, role: int):
        pass


    async def on_voice_state_update(self, member, before, after):
        if member.guild in self.guilds and after.channel.id in channels(member.guild) and not before.channel == after.channel:
            await self.selfchannel.send(content='True')
            # await self.channel.send(content='Client {0.name} has changed voice state.\n\
            # Previous channel: {1.channel}\nNew channel: {2.channel}'.format(member, before, after))

        #     role = discord.utils.get(self.selfguild.roles, id=320707150219444234)
        #     try:
        #         if after.channel is not None:
        #             if "VC - GTA V" not in [r.name for r in member.roles]:
        #                 await member.add_roles(role)
        #         else:
        #             await member.remove_roles(role)
        #     except:
        #         with exception as e:
        #             print(e.__name__, str(e))
        # else:
        #     pass



def setup(bot):
    bot.add_cog(VCAccess(bot))
