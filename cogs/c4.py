"""Connect Four
Written for Python 3.6 and discord.py 1.0.0a"""

import discord
from discord.ext import commands
from .utils import checks
from main import app_name


# class Player:
#     """Board Game Participant"""
#     def __init__(self, member: discord.Member):
#         self.member = member
#
#     @property
#     def name(self):
#         return self.member.name
#
#     @property
#     def color(self):
#         return self.member.color
#
#     @property
#     def id(self):
#         return self.member.id
#
#     @property
#     def default_avatar(self):
#         return self.member.default_avatar


class Session:
    """Active Session of Connect Four"""
    def __init__(self, p1, p2):
        self.p1 = p1  # These will be discord.Member objects of players
        self.p2 = p2  # `p1` being ctx.author and `p2 being the ping
        self.board = [[0 for x in range(7)] for y in range(7)]
        self.turn = 0
        self.timeout = 0
        self.msg = None
        self.emojis = {
            0: "⚪",  # :white_circle:
            self.p1.id: "🔴",  # :red_circle:
            self.p2.id: "🔵",  # :large_blue_circle:
        }

    @property
    def current_player(self):
        if self.turn % 2 == 1:
            return self.p1
        else:
            return self.p2

    @property
    def current_player_chip(self):
        return self.player_chip(self.current_player)

    def player_chip(self, player: discord.Member):
        return self.emojis.get(player.id, 0)

    @property
    def color(self):
        name = self.current_player.default_avatar.name
        if name == "grey":
            name = "light_grey"
        return getattr(discord.Colour, name)()

    def play(self, player, row):
        self.board[row][self.board[row][-1]] = player
        self.board[row][-1] += 1
        self.turn += 1
        return self.check([self.board[x][:-1] for x in range(7)])

    @property
    def get_board(self):
        board = []
        for row in self.board:
            board.append([self.emojis[i] for i in row[:-1]][::-1])

        return "\n".join(["{}{}{}{}{}{}{}".format(*[board[y][x] for y in range(7)]) for x in range(6)])

    def check(self, board):
        for x in range(7):
            for y in range(3):
                if board[x][y] != 0 and \
                                board[x][y] == board[x][y + 1] and \
                                board[x][y] == board[x][y + 2] and \
                                board[x][y] == board[x][y + 3]:
                    return self.p1 if board[x][y] == self.p1.id else self.p2

        for x in range(4):
            for y in range(6):
                if board[x][y] != 0 and \
                                board[x][y] == board[x + 1][y] and \
                                board[x][y] == board[x + 2][y] and \
                                board[x][y] == board[x + 3][y]:
                    return self.p1 if board[x][y] == self.p1.id else self.p2

        for x in range(4):
            for y in range(3):
                if board[x][y] != 0 and \
                                board[x][y] == board[x + 1][y + 1] and \
                                board[x][y] == board[x + 2][y + 2] and \
                                board[x][y] == board[x + 3][y + 3]:
                    return self.p1 if board[x][y] == self.p1.id else self.p2

        for x in range(3, 7):
            for y in range(3):
                if board[x][y] != 0 and \
                                board[x][y] == board[x - 1][y + 1] and \
                                board[x][y] == board[x - 2][y + 2] and \
                                board[x][y] == board[x - 3][y + 3]:
                    return self.p1 if board[x][y] == self.p1.id else self.p2

        if all(map(lambda n: n == 6, [r[6] for r in self.board])):
            return "Draw"

        return None


class ConnectFour:
    """Play a game of Connect Four

    See the help manual for individual
    commands for more information.

    The classic game of Connect Four.
    Use these commands to play a game
    of Connect Four with another user.
    You can have multiple concurrent
    games, one per channel."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.sessions = {}
        self.timeout = 120
        self.timeout_incr = 5
        self.message_icon = ["ℹ", "⚠", "⛔"]  # :information_source:, :warning:, :no_entry:
        self.message_color = [discord.Colour.blue(), discord.Colour.orange(), discord.Colour.red()]

    def session(self, ctx):
        return self.sessions.get(ctx.channel.id, None)

    def chan_check(self, ctx):
        return str(ctx.channel.id) in self.db.smembers(f"{app_name}:c4:allowed_channels")

    async def member_check(self, ctx, member):
        try:
            return await commands.converter.MemberConverter().convert(ctx, member)
        except (commands.BadArgument, commands.NoPrivateMessage):
            return None

    async def message(self, ctx, msg="Error", level=0):
        em = discord.Embed(description=f"{self.message_icon[level]}  {msg}", color=self.message_color[level])
        await ctx.send(embed=em)

    async def send_board(self, ctx, init=False, win=None):
        session = self.session(ctx)
        session.ctx = ctx
        if session.msg is not None:
            await session.msg.delete()

        if win:
            if win == "Draw":
                turn = f"Game ended in a Draw."
                color = discord.Colour.dark_grey()
            elif win == "Forfeit":
                turn = f"Game Over. {ctx.author.name} Forfeits."
                color = discord.Colour.dark_grey()
            elif win == "Timeout":
                turn = f"Time Out. {session.current_player.name} Forfeits."
                color = discord.Colour.dark_grey()
            else:
                turn = f"Game Over!\n{win.name} wins! 🎉"
                color = 0xFDFF00
        else:
            turn = "New game!" if init else f"Turn: {(session.turn + 2) // 2}"
            color = session.color

        em = discord.Embed(title=f"{session.player_chip(session.p1)}{session.p1.name} 🆚 "
                                 f"{session.p2.name}{session.player_chip(session.p2)}",
                           description=f"{turn}\n\n:one::two::three::four::five::six::seven:\n{session.get_board}",
                           color=color)

        if win:
            self.sessions.pop(ctx.channel.id)
            await ctx.send(embed=em)
        else:
            em.set_footer(text=f"{session.current_player.name}'s turn: {session.current_player_chip}")
            session.msg = await ctx.send(embed=em)

        if not win == "Timeout":
            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()

    @commands.group(name="play")
    async def play(self, ctx):
        """Connect Four

        Use `[p]c4 <column>` to place a piece.
        First to get four in a row, whether
        horizontal, vertical, or diagonal wins."""
        if not self.chan_check(ctx):
            return
        if not ctx.invoked_subcommand:
            await self.bot.formatter.format_help_for(ctx, ctx.command)

    @play.command(name="c4")
    async def _c4(self, ctx, *, user: discord.Member=None):
        """Star a game of Connect Four

        `[p]c4 start @user` will start a game
        with that user in the current channel."""
        if not self.chan_check(ctx):
            return
        if user:
            if user.id == ctx.author.id:
                await self.message(ctx, msg="You cannot start a game with yourself.", level=1)
            else:
                session = self.session(ctx)
                if session:
                    await self.message(ctx, msg="There is already an active game in this channel.", level=2)
                else:
                    self.sessions[ctx.channel.id] = Session(ctx.author, user)
                    await self.send_board(ctx)
        else:
            await self.bot.formatter.format_help_for(ctx, ctx.command, "You need another player to start.")

    @commands.group(name="c4", invoke_without_command=True)
    async def c4(self, ctx, *, arg=None):
        """Make a Move

        `[p]c4 <column>` will place a chip
        in that row. Only the current player
        can use this command."""
        if not self.chan_check(ctx):
            return
        member = await self.member_check(ctx, arg)
        if member:
            ctx.message.content = f"{self.bot.command_prefix[0]}c4 play {member.mention}"
        else:
            ctx.message.content = f"{self.bot.command_prefix[0]}c4 move {arg}"
        await self.bot.process_commands(ctx.message)

    @c4.command(name="play", hidden=True)
    async def c4_play(self, ctx, *, user: discord.Member=None):
        """Star a game of Connect Four

        `[p]c4 start @user` will start a game
        with that user in the current channel."""
        if not self.chan_check(ctx):
            return
        if user:
            if user.id == ctx.author.id:
                await self.message(ctx, msg="You cannot start a game with yourself.", level=1)
            else:
                session = self.session(ctx)
                if session:
                    await self.message(ctx, msg="There is already an active game in this channel.", level=2)
                else:
                    self.sessions[ctx.channel.id] = Session(ctx.author, user)
                    await self.send_board(ctx)
        else:
            await self.bot.formatter.format_help_for(ctx, ctx.command, "You need another player to start.")

    @c4.command(name="quit", aliases=["end"])
    async def c4_quit(self, ctx):
        """Quits an active game of Connect Four

        `[p]c4 quit` can be used by either player
        to quit their game in the channel."""
        if not self.chan_check(ctx):
            return
        session = self.session(ctx)
        if session and ctx.author in [session.p1, session.p2]:
            await self.send_board(ctx, win="Forfeit")
        else:
            await self.message(ctx, msg="No active game in this channel.", level=1)

    @c4.command(name="board")
    async def c4_board(self, ctx):
        """Resends the current board

        Can be used if the board gets lost in the chat"""
        if not self.chan_check(ctx):
            return
        session = self.sessions.get(ctx.channel.id, None)
        if session and ctx.author in [session.p1, session.p2]:
            await self.send_board(ctx)
        else:
            await self.message(ctx, msg="No active game in this channel.", level=1)

    @c4.command(name="move")
    async def c4_move(self, ctx, row: int):
        """Make a Move

        `[p]c4 <column>` will place a chip
        in that row. Only the current player
        can use this command."""
        if not self.chan_check(ctx):
            return
        row -= 1
        session = self.session(ctx)
        if session:
            if ctx.author == session.current_player:
                if row in range(7):
                    if session.board[row][-1] < 6:
                        check = session.play(ctx.author.id, row)
                        await self.send_board(ctx, win=check)
                    else:
                        await self.message(ctx, "That row is full. Select another.", level=2)
                else:
                    await self.message(ctx, "Invalid row number. Select another.", level=2)
        else:
            await self.message(ctx, msg="No active game in this channel.", level=1)

    @checks.sudo()
    @c4.command(name="enable", hidden=True)
    async def c4_enable(self, ctx, *, chan: discord.TextChannel=None):
        if not chan:
            chan = ctx.channel
        if self.db.sadd(f"{app_name}:c4:allowed_channels", chan.id):
            await self.message(ctx, msg="Connect Four successfully enabled on channel.")
        else:
            await self.message(ctx, msg="Connect Four already enabled on channel.", level=1)

    @checks.sudo()
    @c4.command(name="disable", hidden=True)
    async def c4_disable(self, ctx, *, chan: discord.TextChannel=None):
        if not chan:
            chan = ctx.channel
        if self.db.srem(f"{app_name}:c4:allowed_channels", chan.id):
            await self.message(ctx, msg="Connect Four successfully disabled on channel.")
        else:
            await self.message(ctx, msg="Connect Four already disabled on channel.", level=1)

    @checks.sudo()
    @c4.command(name="games", hidden=True)
    async def c4_games(self, ctx):
        await self.message(ctx, msg=f"Total running games: {len(self.sessions.keys())}")

    @checks.sudo()
    @c4.command(name="kill", hidden=True)
    async def c4_kill(self, ctx, *, _all: bool=False):
        """Aministrative kill command

        This will kill all running games of
        Connect Four in all channels."""
        if not _all:
            if self.sessions.pop(ctx.channel.id, None):
                await self.message(ctx, msg="Current game in this channel has been terminated.")
            else:
                await self.message(ctx, msg="No active game in this channel.", level=1)
        else:
            await self.message(ctx, msg=f"All running games have been terminated. (Total: {len(self.sessions.keys())})")
            self.sessions = {}

    @checks.sudo()
    @c4.command(name="killall", hidden=True)
    async def c4_killall(self, ctx):
        ctx.message.content = f"{self.bot.command_prefix[0]}kill True"
        await self.bot.process_commands(ctx.message)

    async def on_timer_update(self, sec):
        if sec % self.timeout_incr == 0:
            sessions = [s for s in self.sessions.values()]
            for session in sessions:
                session.timeout += self.timeout_incr
                if session.timeout == self.timeout:
                    await self.send_board(session.ctx, win="Timeout")


def setup(bot):
    bot.add_cog(ConnectFour(bot))
