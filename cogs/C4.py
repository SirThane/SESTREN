"""Connect Four
Written for Python 3.6 and discord.py 1.0.0a"""

import discord
from discord.ext import commands
from .utils import checks


class Session:
    """Active Session of Connect Four"""
    def __init__(self, p1, p2, chan):
        self.p1 = p1  # These will be discord.Member objects of players
        self.p2 = p2  # `p1` being ctx.author and `p2 being the ping
        self.chan = chan
        self.board = [[0 for x in range(7)] for y in range(7)]
        self.turn = 0
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

        return board

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

        if all(map(lambda x: x == 6, [r[6] for r in self.board])):
            return "Draw"

        return False


class ConnectFour:
    """Play a game of Connect Four"""
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}

    def session(self, ctx):
        return self.sessions.get(ctx.channel.id, None)

    async def c4_error(self, ctx, msg="Error"):
        em = discord.Embed(description=f"⛔ {msg}", color=discord.Colour.red())
        await ctx.send(embed=em)

    async def send_board(self, ctx, init=False, win=False):
        session = self.session(ctx)
        if session.msg is not None:
            try:
                await session.msg.delete()
            except Exception as e:
                await ctx.send(f"{type(e)}: {e}")

        board = session.get_board
        parsed_board = "\n".join(["{}{}{}{}{}{}{}".format(*[board[y][x] for y in range(7)]) for x in range(6)])

        if win:
            if win == "Draw":
                turn = f"Game ended in a Draw."
            else:
                turn = f"Game Over!\n{win.name} wins! 🎉"
        else:
            turn = "New game!" if init else f"Turn: {(session.turn + 2) // 2}"

        em = discord.Embed(title=f"{session.player_chip(session.p1)}{session.p1.name} 🆚 "
                                 f"{session.p2.name}{session.player_chip(session.p2)}",
                           description=f"{turn}\n\n:one::two::three::four::five::six::seven:\n{parsed_board}",
                           color=session.color)

        if win:
            self.sessions.pop(ctx.channel.id)
            await ctx.send(embed=em)
        else:
            em.set_footer(text=f"{session.current_player.name}'s turn: {session.current_player_chip}")
            session.msg = await ctx.send(embed=em)

        await ctx.message.delete()

    @commands.group()
    async def c4(self, ctx):
        """Connect Four

        The classic game of Connect Four.
        Use these commands to play a game
        of Connect Four with another user.
        You can have multiple concurrent
        games, one per channel."""
        if not ctx.invoked_subcommand:
            await self.bot.formatter.format_help_for(ctx, ctx.command)

    @c4.command(name="start", aliases=["play"])
    async def _start(self, ctx, *, user: discord.Member=None):
        """Star a game of Connect Four

        `[p]c4 start @user` will start a game
        with that user in the current channel."""
        # if user:
        #     await ctx.send(f"Ping! Confirmed user: {user.name} (Currently not implemented)")
        if user:
            session = self.session(ctx)
            if session:
                await self.c4_error(ctx, msg="There is already an active game in this channel.")
            else:
                self.sessions[ctx.channel.id] = Session(ctx.author, user, ctx.channel)
                await self.send_board(ctx)
        else:
            await self.bot.formatter.format_help_for(ctx, ctx.command, "You need another player to start.")

    @c4.command(name="quit", aliases=["end"])
    async def _quit(self, ctx):
        """Quits an active game of Connect Four

        `[p]c4 quit` can be used by either player
        to quit their game in the channel."""
        session = self.sessions.get(ctx.channel.id, None)
        if session and ctx.author in [session.p1, session.p2]:
            self.sessions.pop(ctx.channel.id)
            await ctx.send("Game has ended.")
        else:
            await self.c4_error(ctx, msg="No active game in this channel.")

    @c4.command(name="board")
    async def board(self, ctx):
        """Resends the current board

        Can be used if the board gets lost in the chat"""
        session = self.sessions.get(ctx.channel.id, None)
        if session and ctx.author in [session.p1, session.p2]:
            await self.send_board(ctx)
        else:
            await self.c4_error(ctx, msg="No active game in this channel.")

    @checks.sudo()
    @c4.command(name="kill", aliases=["killall"])
    async def _kill(self, ctx):
        """Aministrative kill command

        This will kill all running games of
        Connect Four in all channels."""
        em = discord.Embed(description=f"All running games have been terminated. (Total: {len(self.sessions.keys())})",
                           color=discord.Colour.dark_grey())
        self.sessions = {}
        await ctx.send(embed=em)

    @checks.sudo()
    @c4.command(name="games")
    async def games(self, ctx):
        em = discord.Embed(description=f"Total running games: {len(self.sessions.keys())}",
                           color=discord.Colour.dark_grey())
        await ctx.send(embed=em)

    @c4.command(name="move")
    async def _move(self, ctx, row: int):
        """Make a Move

        `[p]c4 move <row>` will place a chip
        in that row. Only the current player
        can use this command."""
        row -= 1
        session = self.session(ctx)
        if session:
            if ctx.author == session.current_player:
                if row in range(7):
                    if session.board[row][-1] < 6:
                        check = session.play(ctx.author.id, row)
                        await self.send_board(ctx, win=check)
                    else:
                        await self.c4_error(ctx, "That row is full. Select another.")
                else:
                    await self.c4_error(ctx, "Invalid row number. Select another.")
        else:
            await self.c4_error(ctx, msg="No active game in this channel.")


def setup(bot):
    bot.add_cog(ConnectFour(bot))
