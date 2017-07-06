from discord.ext import commands
import discord
from main import db, name


config = f'{name}:config:permissions'


"""
    These will be internal checks (predicates) for this module.
"""

class Predicates:
    """These will be internal checks (predicates) for this module."""

    @staticmethod
    def precede(precedent):
        def supercede(supercedent):
            def check(ctx):
                return precedent(ctx) or supercedent(ctx)
            return check
        return supercede

    @staticmethod
    async def bot_owner(ctx):
        return await ctx.bot.is_owner(ctx.author)

    @staticmethod
    @precede(bot_owner)
    def sudoer(ctx):
        return ctx.author in db.smembers(f'{config}:sudoers')

    @staticmethod
    @precede(sudoer)
    def modrole(ctx):
        role = db.hget(f'{config}:modrole', f'{ctx.guild.id}')
        if role:
            pass  # TODO: FIX THIS


    @staticmethod
    def has_role(ctx, check):
        """
        Check if someone has a role,
        :param ctx:
        :param check: Prepped find() argument
        :return: Whether or not the role was found
        """
        message = ctx.message
        if Predicates.bot_owner(message):
            return True

        ch = ctx.message.channel
        author = ctx.message.author
        if isinstance(ch, discord.DMChannel):
            return False  # can't have roles in PMs

        # Take a prepped find() argument and pass it in
        role = discord.utils.find(check, author.roles)
        return role is not None

    # @staticmethod
    # def r_pokemon_check(guild):
    #     return guild.id == 111504456838819840

    # @staticmethod
    # def r_md_check(guild):
    #     return guild.id == 117485575237402630

    # @staticmethod
    # def mod_server_check(guild):
    #     return guild.id == 146626123990564864


class Checks:
    """These will be the decorators for commands."""

    @staticmethod
    def owner():
        def predicate(ctx):
            return Predicates.bot_owner(ctx)
        return commands.check(predicate)

    @staticmethod
    def sudo():
        def predicate(ctx):
            return Predicates.sudoer(ctx)
        return commands.check(predicate)

    @staticmethod
    def in_pm():
        def predicate(ctx):
            return isinstance(ctx.channel, discord.DMChannel)
        return commands.check(predicate)

    @staticmethod
    def can_tag():
        def predicate(ctx):
            message = ctx.message
            if Predicates.bot_owner(ctx):
                return True
            elif message.author.id in []:
                return True
            else:
                return False
        return commands.check(predicate)

    # @staticmethod
    # def is_pokemon_mod():
    #     def predicate(ctx):
    #         return Predicates.has_role(ctx, lambda r: r.id == 278331223775117313)
    #     return commands.check(predicate)

    # @staticmethod
    # def r_pokemon():
    #     """Check if it's the /r/pokemon server"""
    #     def predicate(ctx):
    #         return ctx.message.guild is not None and ctx.message.guild.id == 111504456838819840
    #     return commands.check(predicate)

    # @staticmethod
    # def r_md():
    #     """Check if it's the Pokemon Mystery Dungeon server"""
    #     def predicate(ctx):
    #         return ctx.message.guild is not None and ctx.message.guild.id == 117485575237402630
    #     return commands.check(predicate)

    # @staticmethod
    # def not_in_oaks_lab():
    #     def predicate(ctx):
    #         return isinstance(ctx.message.channel, discord.DMChannel) or\
    #                (ctx.message.guild is not None and ctx.message.guild.id != 204402667265589258)
    #     return commands.check(predicate)

    # @staticmethod
    # def not_in_pokemon():
    #     def predicate(ctx):
    #         return isinstance(ctx.message.channel, discord.DMChannel) or
    #           (ctx.message.guild is not None and ctx.message.guild.id != 111504456838819840)
    #     return commands.check(predicate)

    # @staticmethod
    # def mod_server():
    #     def predicate(ctx):
    #         return mod_server_check(ctx.message.guild) or bot_owner(ctx)
    #     return commands.check(predicate)

    # @staticmethod
    # def is_regular():
    #     # Hope you've been eating your fiber
    #     def predicate(ctx):
    #         return not r_pokemon_check(ctx.message.guild) or (r_pokemon_check(ctx.message.guild) and
    #                                                           has_role(ctx, lambda r: r.id == 117242433091141636))
    #     return commands.check(predicate)
