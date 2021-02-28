# -*- coding: utf-8 -*-

"""Custom Exception definitions"""


from discord.ext.commands.errors import CommandError


class UnimplementedError(CommandError):
    """Exception raised when a command is called
    using a feature that has not yet been
    implemented"""
