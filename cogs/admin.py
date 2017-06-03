"""
Administrative commands for pory. A lot of them used from my HockeyBot,
which in turn were mostly from Danny.
Copyright (c) 2015 Rapptz
"""
from discord.ext import commands
import traceback
# import inspect
from asyncio import sleep


class Admin:

    def __init__(self, bot):
        self.bot = bot
        # self.config = bot.config

    @commands.command(hidden=True, pass_context=True)
    async def load(self, ctx, *, module: str, verbose: bool=False):
        """load a module"""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            if not verbose:
                await ctx.message.channel.send(content='{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.message.channel.send(content=traceback.print_tb(e.__traceback__))
        else:
            await ctx.message.channel.send(content="Module loaded successfully.")

    @commands.command(pass_context=True, hidden=True)
    async def unload(self, ctx, *, module: str):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.message.channel.send(content='{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.channel.send(content='Module unloaded successfully.')

    @commands.command(pass_context=True, name='reload', hidden=True)
    async def _reload(self, ctx, *, module: str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            sleep(1)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.message.channel.send(content='Failed.')
            sleep(1)
            await ctx.message.channel.send(content='{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.channel.send(content='Module reloaded.')

    # Thanks to rapptz
    # @commands.command(hidden=True)
    # async def eval(self, ctx, *, code: str):
    #     """Run eval() on an input."""
    #     import discord
    #     import random
    #     code = code.strip('` ')
    #     python = '```py\n>>> {0}\n{1}\n```'
    #     env = {
    #         'bot': self.bot,
    #         'ctx': ctx,
    #         'message': ctx.message,
    #         'guild': ctx.message.guild,
    #         'channel': ctx.message.channel,
    #         'author': ctx.message.author,
    #         'discord': discord,
    #         'random': random
    #     }
    #
    #     env.update(globals())
    #
    #     try:
    #         result = eval(code, env)
    #         if inspect.isawaitable(result):
    #             result = await result
    #     except Exception as e:
    #         await ctx.message.edit(content=python.format(code, type(e).__name__ + ': ' + str(e)))
    #         return
    #
    #     await ctx.message.edit(content=python.format(code, result))

    # @commands.command(pass_context=True, hidden=True)
    # async def set_config(self, ctx, key: str, value: str):
    #     """Directly alter a config file."""
    #     try:
    #         try:
    #             value = int(value)
    #         except ValueError:
    #             pass
    #         await self.config.put(key, value)
    #         await ctx.message.edit(content="Success.")
    #     except KeyError:
    #         raise commands.CommandInvokeError
    #
    # @commands.command(hidden=True, pass_context=True)
    # async def append_to_config(self, ctx, key: str, value: str):
    #     """Append a value to a list in a config file"""
    #     try:
    #         temp_list = await self.config.get(key)
    #         temp_list.append(value)
    #         await self.config.put(key, temp_list)
    #         await ctx.message.edit(content="Success.")
    #     except KeyError:
    #         await ctx.message.edit(content="Key {} not found.".format(key))
    #
    # @commands.command(pass_context=True, hidden=True, aliases=["rip", "F", "f"])
    # async def kill(self, ctx):
    #     log.warning("Restarted by command.")
    #     await ctx.message.edit(content="Restarting.")
    #     await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
