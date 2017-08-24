import asyncio
import discord
# import operator
# import math
import datetime
from discord.ext import commands
from main import app_name


config = f'{app_name}:activity'


# ranks = {
#     10: [1, "Beginner"],
#     69: [2, "Memer Rank 1"],
#     300: [3, "Talker"],
#     360: [4, "MLG'er"],
#     420: [5, "Memer Rank 2"],
#     666: [6, "Devil"],
#     1000: [7, "Active"],
#     1337: [8, "1337"],
#     3000: [9, "Really Active"],
#     6000: [10, "Extremely Active"],
#     9001: [11, "Memer Rank 3"],
#     10000: [12, "Too Active"]
# overrides = set()


class UserActivity:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.cooldown = set()

    async def check_cooldown(self, user):
        if user.bot:
            return True
        # if user.id in overrides:
        #     return False
        return user.id in self.cooldown or user.id == self.bot.user.id

    async def put_cooldown(self, user, dur: int=15):
        # if user.id in overrides:
        #     return
        self.cooldown.add(user.id)
        await asyncio.sleep(dur)
        self.cooldown.remove(user.id)

    async def on_message(self, m):
        if not isinstance(m.channel, discord.DMChannel) and not isinstance(m.channel, discord.GroupChannel):
            return

        if not self.db.sismember(f'{config}:guilds', m.guild.id):
            return

        if await self.check_cooldown(m.author):
            return

        self.db.sadd(f'{config}:users', f'{m.author.id}')

        try:
            user_metrics = self.db.hgetall(f'{config}:users:time:{m.author.id}')
        except:
            user_metrics = {
                'total': 0,
                '0': 0, '1': 0, '2': 0, '3': 0,
                '4': 0, '5': 0, '6': 0, '7': 0,
                '8': 0, '9': 0, '10': 0, '11': 0,
                '12': 0, '13': 0, '14': 0, '15': 0,
                '16': 0, '17': 0, '18': 0, '19': 0,
                '20': 0, '21': 0, '22': 0, '23': 0,
            }

        self.db.hmset(f'{config}:users:{m.author.id}', user_metrics)

        self.bot.loop.create_task(self.put_cooldown(m.author))

    # def next_ranks(self, num):
    #     e = []
    #     for rank in ranks.keys():
    #         if int(rank) > int(num):
    #             e.append(ranks[rank][1])
    #     if len(e) == 0:
    #         e = ["Nothing left to do!!!"]
    #     return e

    # def next_rank(self, num):
    #     for i in range(100000):
    #         try:
    #             if ranks[num + i]:
    #                 return [ranks[num + i], num + i]
    #         except:
    #             continue
    #
    #     return [[69, "Nothing"], 10000]

    # @commands.command(name='rank', hidden=True, disabled=True)
    # async def rank(self, ctx, user: discord.Member=None):
    #     """Get someones rank"""
    #     if user is None:
    #         user = ctx.author
    #     d = self.db.hget('rankcount', user.id)
    #     if d is None:
    #         em = discord.Embed(title="No Data", description="Try get them to speak a little more!!!")
    #         await ctx.send(embed=em)
    #     else:
    #         em = discord.Embed(title=f"{str(user)}'s info")
    #         em.set_thumbnail(url=user.avatar_url)
    #         em.add_field(name="PyPoint count", value=f"{d} PyPoints")
    #         em.add_field(name="Current Rank", value=self.db.hget('currank', user.id))
    #         y = self.next_rank(int(d))
    #         prcnt = 'nil'  # math.floor((int(d) / int(y[1])) * 100)
    #         if y[0][0] == 69:
    #             em.add_field(name="Next Rank", value=f"Nothing left to do")
    #         else:
    #             em.add_field(name="Next Rank", value=f"Level {y[0][0]} - {y[0][1]}, {str(d)}/{y[1]} ({prcnt}%) there")
    #
    #         await ctx.send(embed=em)

    # @commands.command(name='leaderboard', hidden=True, disabled=True)
    # async def leaderboard(self, ctx):
    #     """Get the rank leaderboard"""
    #     em = discord.Embed(title="Please wait", description="Compiling sources and generating leaderboard...")
    #     message = await ctx.send(embed=em)
    #     lb = self.db.hgetall("rankcount")
    #     lb = {k: int(v) for k, v in lb.items()}
    #     lb = sorted(lb.items(), key=operator.itemgetter(1), reverse=True)
    #     _message = ""
    #     for i in range(0, 10):
    #         user = await self.bot.get_user_info(int(lb[i][0]))
    #         currank = self.db.hget("currank", str(user.id))
    #         _message += f"{i + 1}. {str(user)} - {lb[i][1]} PyPoints - Current Rank: {currank}\n"
    #     await message.delete()
    #     em = discord.Embed(title="Rank leaderboard", description=_message)
    #     await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(UserActivity(bot))
