from discord.ext import commands
from .utils import checks
import traceback
import discord
import inspect
from contextlib import redirect_stdout
import io
import subprocess


class REPL:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.sessions = set()
        self.shellsessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        return '{0.text}{1:>{0.offset}}\n{2}: {0}'.format(e, '^', type(e).__name__)

    @commands.command(name='repl')
    @checks.sudo()
    async def repl(self, ctx):
        msg = ctx.message
        members = self.bot.get_all_members()  # Generator of all members on all servers. guild.members instead?

        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': msg,
            'server': msg.guild,
            'channel': msg.channel,
            'author': msg.author,
            '_': None,
            'checks': checks,
            'db': self.db,
            'joseph': discord.utils.get(members, id="165023948638126080")
        }

        if msg.channel.id in self.sessions:
            em = discord.Embed(title="Already Running", description="REPL already active in this channel")
            await ctx.send(embed=em)
            return

        self.sessions.add(msg.channel.id)
        em = discord.Embed(title="Started", description="Type `exit` or `quit` to end")
        await ctx.send(embed=em)

        while True:
            response = await self.bot.wait_for('message',
                                               check=lambda m: m.content.startswith('`') and m.channel == msg.channel
                                               and m.author.id in checks.ownerids)

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                em = discord.Embed(title="Ending", description="Stopping REPL Session")
                await ctx.send(embed=em)
                self.sessions.remove(msg.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if "while True" in cleaned:
                return await ctx.send(embed=discord.Embed(title="Failsafe activated",
                                                          description="For server reliability I have blocked that code"
                                                                      "as it contains a while loop"))

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    em = discord.Embed(title="Error", description=self.get_syntax_error(e), colour=discord.Colour.red())
                    await ctx.send(embed=em)
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)  # var code may be referenced before assignment
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                if self.bot.http.token in value:
                    fmt = "```py\nNot so fast ( ͡° ͜ʖ ͡°)\n```"
                else:
                    fmt = '```py\n{}{}\n```'.format(value, traceback.format_exc())
                c = discord.Colour.red()
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = '```py\n{}{}\n```'.format(value, result)
                    variables['_'] = result
                elif value:
                    fmt = '```py\n{}\n```'.format(value)
                try:
                    fmt = fmt.replace(self.bot.http.token,"Not so fast ( ͡° ͜ʖ ͡°)")
                except:
                    fmt = fmt
                c = discord.Colour.green()

            try:
                if fmt is not None:
                    if len(str(fmt)) > 2000:
                        em = discord.Embed(title="Too long", description="Content too long")
                        await ctx.send(embed=em)
                    else:
                        em = discord.Embed(title="Results", description=fmt, colour=c)
                        await ctx.send(embed=em)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                em = discord.Embed(title="Unexpected error", description=e, colour=discord.Colour.red())
                await ctx.send(embed=em)

    @commands.command(name='replshell')
    @checks.sudo()
    async def replshell(self, ctx):
        """Run code in Discord from REPL"""
        msg = ctx.message
        if msg.channel.id in self.shellsessions:
            em = discord.Embed(title="Running", description="Session already running")
            await ctx.send(embed=em)
            return
        em = discord.Embed(title="Starting")  # , description="")
        await ctx.send(embed=em)
        self.shellsessions.add(msg.channel.id)
        while True:
            response = await self.bot.wait_for('message', check=lambda m: checks.sudoer(m.context))
            exit_words = ['exit', 'close', 'stop', 'quit']
            for word in exit_words:
                if word in response.content:
                    em = discord.Embed(title="Stopping", description="Stopping REPLShell")
                    await ctx.send(embed=em)
                    self.shellsessions.remove(response.channel.id)
                    return
            try:
                f = subprocess.check_output(response.content, shell=True).decode()
                em = discord.Embed(title="Results", description=f, colour=discord.Colour.green())
                await ctx.send(embed=em)
            except Exception as e:

                em = discord.Embed(title="Non-zero code", description=str(e), colour=discord.Colour.red())
                await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(REPL(bot))
