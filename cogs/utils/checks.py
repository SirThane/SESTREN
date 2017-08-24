from discord.ext import commands
import discord
from main import db, app_name

"""
    Utility functions and definitions.
"""


config = f'{app_name}:config:permissions'


def supercede(precedent):
    """Decorate a predicate.
    Pass a predicate as param.
    Returns True if either test True."""
    def decorator(predicate):
        def wrapper(ctx):
            if precedent(ctx):
                return True
            return predicate(ctx)
        return wrapper
    return decorator


def require(requisite):
    """Decorate a predicate.
    Pass a predicate as param.
    Returns False if either test False."""
    def decorator(predicate):
        def wrapper(ctx):
            if not requisite(ctx):
                return False
            return predicate(ctx)
        return wrapper
    return decorator


def in_pm(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or isinstance(ctx.channel, discord.GroupChannel)


def no_pm(ctx):
    return not in_pm(ctx)


"""
    These will be internal checks (predicates) for this module.
"""


def bot_owner(ctx):
    def check():
        return ctx.author.id == 125435062127820800
    return check()


@require(no_pm)  # can't have roles in PMs
@supercede(bot_owner)
def has_role(ctx, check):
    """
    Check if someone has a role,
    :param ctx:
    :param check: Prepped find() argument
    :return: Whether or not the role was found
    """
    # Take a prepped find() argument and pass it in
    return discord.utils.find(check, ctx.author.roles) is not None


@supercede(bot_owner)
def sudoer(ctx):
    return ctx.author in db.smembers(f'{config}:sudoers')


@supercede(sudoer)
def adminrole(ctx):  # TODO: WIP
    role = db.hget(f'{config}:adminrole', f'{ctx.guild.id}')
    if role:
        return has_role(ctx, lambda r: r.id == int(role))
    else:
        return False


@supercede(sudoer)
def modrole(ctx):  # TODO: WIP
    role = db.hget(f'{config}:modrole', f'{ctx.guild.id}')
    if role:
        return has_role(ctx, lambda r: r.id == int(role))
    else:
        return False


# ### Luc's Predicates ###
#
# def r_pokemon_check(guild):
#     return guild.id == 111504456838819840
#
#
# def r_md_check(guild):
#     return guild.id == 117485575237402630
#
#
# def mod_server_check(guild):
#     return guild.id == 146626123990564864


"""
    The functions that will decorate commands.
"""


def owner():
    def predicate(ctx):
        return bot_owner(ctx)
    return commands.check(predicate)


def sudo():
    def predicate(ctx):
        return sudoer(ctx)
    return commands.check(predicate)


def pm(allow=False):
    def decorator(check):
        def predicate(ctx):
            return in_pm(ctx)
        return commands.check(predicate)


# ### Luc's checks ###
#
# @supercede(bot_owner)
# def can_tag():
#     def predicate(ctx):
#         return ctx.author.id in []
#     return commands.check(predicate)
#
#
# def is_pokemon_mod():
#     def predicate(ctx):
#         return has_role(ctx, lambda r: r.id == 278331223775117313)
#     return commands.check(predicate)
#
#
# @require(no_pm)
# def r_pokemon():
#     """Check if it's the /r/pokemon server"""
#     def predicate(ctx):
#         return ctx.message.guild.id == 111504456838819840
#     return commands.check(predicate)
#
#
# @require(no_pm)
# def r_md():
#     """Check if it's the Pokemon Mystery Dungeon server"""
#     def predicate(ctx):
#         return ctx.message.guild is not None and ctx.message.guild.id == 117485575237402630
#     return commands.check(predicate)
#
#
# @require(no_pm)
# def not_in_oaks_lab():
#     def predicate(ctx):
#         return ctx.message.guild.id != 204402667265589258
#     return commands.check(predicate)
#
#
# @require(no_pm)
# def not_in_pokemon():
#     def predicate(ctx):
#         return ctx.message.guild.id != 111504456838819840
#     return commands.check(predicate)
#
#
# @supercede(bot_owner)
# def mod_server():
#     def predicate(ctx):
#         return mod_server_check(ctx.message.guild)
#     return commands.check(predicate)


# def is_regular():
#     # Hope you've been eating your fiber
#     def predicate(ctx):
#         return not r_pokemon_check(ctx.message.guild) or (r_pokemon_check(ctx.message.guild) and
#                                                           has_role(ctx, lambda r: r.id == 117242433091141636))
#     return commands.check(predicate)
