# -*- coding: utf-8 -*-

"""Cog containing all global bot events"""


# Lib
from datetime import datetime

# Site
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.errors import (
    CheckFailure,
    CommandError,
    CommandInvokeError,
    CommandNotFound,
    DisabledCommand,
    MissingRequiredArgument,
    NoPrivateMessage
)
from discord.message import Message
from pytz import timezone
from typing import Union

# Local
from utils.classes import Bot, Embed, SubRedis
from utils.errors import UnimplementedError


WELCOME = "**Welcome to AWBW Discord Server {}!**\nPresent yourself and have fun!"
LEAVE = "**{} has left our army...**\nBe happy in peace."


tz = timezone('America/Kentucky/Louisville')


class Events(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = SubRedis(bot.db, "events")

        self.errorlog = bot.errorlog

        # self.awbw = bot.get_guild(313453805150928906)               # AWBW Guild
        # self.channel = bot.get_channel(313453805150928906)          # AWBW General
        self.notifchannel = bot.get_channel(815627325936631848)     # SESTREN-Notifs

    # @Cog.listener(name="on_member_join")
    # async def on_member_join(self, member: Member):
    #     """Welcome Message"""
    #
    #     if not self.awbw:
    #         return
    #     if member.guild.id != self.awbw.id:
    #         return
    #     em = Embed(
    #         description=WELCOME.format(member.display_name),
    #         color=member.guild.me.colour
    #     )
    #     await self.channel.send(embed=em)

    # @Cog.listener(name="on_member_remove")
    # async def on_member_remove(self, member: Member):
    #     """Leaver Message"""
    #
    #     if not self.awbw:
    #         return
    #     if member.guild.id != self.awbw.id:
    #         return
    #     em = Embed(
    #         description=LEAVE.format(member.display_name),
    #         color=member.guild.me.colour
    #     )
    #     await self.channel.send(embed=em)

    # @Cog.listener(name="on_message")
    # async def on_message(self, message: discord.Message) -> None:
    #     if "airport" in message.content.lower():
    #         await message.add_reaction(self.sad_andy)

    @Cog.listener(name="on_command_error")
    async def on_command_error(self, ctx: Context, error: Union[Exception, CommandError]):
        if isinstance(error, NoPrivateMessage):
            em = Embed(
                color=Embed.Empty,
                title="Command Error",
                description="```\n"
                            "This command cannot be used in private messages.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, DisabledCommand):
            em = Embed(
                color=ctx.guild.me.colour,
                title="Command Error",
                description="```\n"
                            "This command is disabled and cannot be used.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, MissingRequiredArgument):
            await self.bot.help_command.send_help_for(ctx, ctx.command, "You are missing required arguments.")

        elif isinstance(error, CommandNotFound):
            await self.bot.help_command.send_help_for(
                ctx,
                self.bot.get_command("help"),
                f"Command `{ctx.invoked_with}` not found."
            )

        elif isinstance(error, CheckFailure):
            em = Embed(
                color=ctx.guild.me.colour,
                title="Permissions Error",
                description="```\n"
                            "You do not have the appropriate access for that command.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, UnimplementedError):
            em = Embed(
                color=ctx.guild.me.colour,
                title="Command Error",
                description="```\n"
                            "This feature has not yet been implemented.\n"
                            "```"
            )
            await ctx.send(embed=em)

        elif isinstance(error, CommandInvokeError):
            await self.errorlog.send(error.original, ctx)

        else:
            await self.errorlog.send(error)

    @Cog.listener("on_message")
    async def on_message(self, msg: Message):
        if str(self.bot.user.id) in msg.content:
            ts = tz.localize(datetime.now()).strftime("%b. %d, %Y %I:%M %p")
            author = msg.author
            display_name = f' ({author.display_name})' if author.display_name != author.name else ''
            em = Embed(
                title=f"{msg.guild}: #{msg.channel} at {ts}",
                description=msg.content,
                color=author.colour
            )
            em.set_author(
                name=f"{author.name}#{author.discriminator}{display_name}",
                icon_url=author.avatar_url_as(format="png")
            )
            await self.notifchannel.send(msg.jump_url, embed=em)


def setup(bot: Bot):
    """Events"""
    bot.add_cog(Events(bot))
