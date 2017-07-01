"""
Mostly stolen from Luc:
    Administrative commands for pory. A lot of them used from my HockeyBot,
    which in turn were mostly from Danny.

Copyright (c) 2015 Rapptz
"""
from discord.ext import commands
import discord
import random
import traceback
import inspect
import logging
from asyncio import sleep
import sys
from io import StringIO
import contextlib
from cogs.utils import checks

log = logging.getLogger()


@contextlib.contextmanager
def stdoutio(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class Admin:

    def __init__(self, bot):
        self.bot = bot
        # self.config = bot.config

    def env(self, ctx):
        import random
        environment = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.guild,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'discord': discord,
            'random': random
        }
        environment.update(globals())
        return environment

    @checks.sudo()
    @commands.command(hidden=True)
    async def load(self, ctx, *, cog: str, verbose: bool=False):
        """load a module"""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            if not verbose:
                await ctx.send(content='{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.send(content=traceback.print_tb(e.__traceback__))
        else:
            await ctx.send(content="Module loaded successfully.")

    @checks.sudo()
    @commands.command(hidden=True)
    async def unload(self, ctx, *, cog: str):
        """Unloads a module."""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(content='{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send(content='Module unloaded successfully.')

    @checks.sudo()
    @commands.command(hidden=True)
    async def reload(self, ctx, *, cog: str):
        """Reloads a module."""
        cog = 'cogs.{}'.format(cog)
        try:
            self.bot.unload_extension(cog)
            await sleep(1)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(content='{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send(content='Module reloaded.')

    @checks.sudo()
    @commands.command(hidden=True, name='await')
    async def _await(self, ctx, *, code):

        env = self.env(ctx)

        try:
            await eval(code, env)
        except Exception as e:
            await ctx.send(str(e))

    # Thanks to rapptz
    @checks.sudo()
    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx, *, code: str):
        """Run eval() on an input."""

        code = code.strip('` ')
        python = '```py\n{0}\n```'
        env = self.env(ctx)

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
            result = str(result)[:1014]
            color = 0x00FF00
            field = {
                'inline': False,
                'name': 'Yielded result:',
                'value': python.format(result)
            }
        except Exception as e:
            color = 0xFF0000
            field = {
                'inline': False,
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': '{0} '.format(e)
            }

        embed = discord.Embed(title="Eval on:", description=python.format(code), color=color)
        embed.add_field(**field)

        await ctx.send(embed=embed)

    @checks.sudo()
    @commands.command(hidden=True, name='exec')
    async def _exec(self, ctx, *, code: str):
        """Run exec() on an input."""

        code = code.strip('```\n ')
        python = '```py\n{0}\n```'

        env = self.env(ctx)

        try:
            with stdoutio() as s:
                exec(code, env)
                result = str(s.getvalue())
            result = str(result)[:1014]
            color = 0x00FF00
            field = {
                'inline': False,
                'name': 'Yielded result(s):',
                'value': python.format(result)
            }
        except Exception as e:
            color = 0xFF0000
            field = {
                'inline': False,
                'name': 'Yielded exception "{0.__name__}":'.format(type(e)),
                'value': str(e)
            }

        embed = discord.Embed(title="Exec on:", description=python.format(code), color=color)
        embed.add_field(**field)

        await ctx.message.delete()
        await ctx.send(embed=embed)

    @checks.sudo()
    @commands.command(name='notif', hidden=True)
    async def notif(self, ctx, channel):
        """Echos custom notification to owner

        This command will typically only be
        invoked by a selfbot."""
        em = ctx.message.embeds.pop(0)
        await ctx.message.delete()
        await ctx.send(f'{ctx.author.mention} <#{channel}>', embed=em)

    @commands.command(name='game', hidden=True)
    async def game(self, ctx, *, game: str=None):
        """
        Changes status to 'Playing <game>'

        [p]game string"""
        if game:
            await self.bot.change_presence(game=discord.Game(name=game))
        else:
            await self.bot.change_presence(game=discord.Game(name=game))
        await ctx.message.edit('Presence updated.')
        sleep(5)
        await ctx.message.delete

    # @commands.command(hidden=True, name='set_config')
    # async def _set_config(self, ctx, key: str, value: str):
    #     """Directly alter a config file."""
    #     try:
    #         try:
    #             value = int(value)
    #         except ValueError:
    #             pass
    #         await self.config.put(key, value)
    #         await ctx.send(content="Success.")
    #     except KeyError:
    #         raise commands.CommandInvokeError
    #
    # @commands.command(hidden=True, name='append_to_config')
    # async def _append_to_config(self, ctx, key: str, value: str):
    #     """Append a value to a list in a config file"""
    #     try:
    #         temp_list = await self.config.get(key)
    #         temp_list.append(value)
    #         await self.config.put(key, temp_list)
    #         await ctx.send(content="Success.")
    #     except KeyError:
    #         await ctx.send(content="Key {} not found.".format(key))

    @commands.command(hidden=True, aliases=["rip", "F", "f"])
    async def kill(self, ctx):  # Overwrites builtin kill()
        log.warning("Restarted by command.")
        await ctx.send(content="Restarting.")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
