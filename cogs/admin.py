"""
Mostly stolen from Luc:
    Administrative commands for pory. A lot of them used from my HockeyBot,
    which in turn were mostly from Danny.

Copyright (c) 2015 Rapptz
"""
from discord.ext import commands
import discord
import traceback
import inspect
import logging
from asyncio import sleep
import sys
import os
from io import StringIO
import contextlib
from cogs.utils import checks
from main import app_name

log = logging.getLogger()
config = f'{app_name}:admin'


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

    def pull(self):
        resp = os.popen("git pull").read()
        resp = f"```diff\n{resp}\n```"
        return resp

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

        await ctx.send(embed=embed)

    @commands.command(name='notif', hidden=True)
    async def notif(self, ctx, *, message: str):
        """Echos custom notification to owner

        This command will typically only be
        invoked by a selfbot."""
        em = ctx.message.embeds.pop(0)
        await ctx.message.delete()
        await ctx.author.send(message, embed=em)

    @checks.sudo()
    @commands.command(name='invite', hidden=True)
    async def invite(self, ctx):
        em = discord.Embed(title=f'OAuth URL for {self.bot.user.name}',
                           description=f'[Click Here]({discord.utils.oauth_url(self.bot.app_info.id)}) '
                                       f'to invite {self.bot.user.name} to your guild.', color=ctx.guild.me.color)
        await ctx.send(embed=em)

    @checks.sudo()
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

    """ It might be cool to make some DB altering commands. """

    @checks.sudo()
    @commands.command(name="pull", hidden=True)
    async def _pull(self, ctx):
        await ctx.send(embed=discord.Embed(title="Git Pull", description=self.pull(), color=0x00FF00))

    @checks.sudo()
    @commands.command(hidden=True, name='restart', aliases=["kill", "f"])
    async def _restart(self, ctx, *, arg=None):  # Overwrites builtin kill()
        log.warning("Restarted by command.")
        if arg.lower() == "pull":
            resp = self.pull()
        await ctx.send(content=f"{resp}\nRestarting by command. . .")
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
