"""Overrides the built-in help formatter.

All help messages will be embed and pretty.

Most of the code stolen from
discord.ext.commands.formatter.py and
converted into embeds instead of codeblocks.

discord.py 1.0.0a

Copyrights to logic of code belong to Rapptz (Danny)"""

import discord
from discord.ext import commands
from discord.ext.commands import formatter
import re
import inspect
import itertools


_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}


_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))


class Help(formatter.HelpFormatter):

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        self.bot.remove_command('help')
        self.bot.formatter = self
        super().__init__(*args, **kwargs)
        # self.bot.formatter = HelpFormatter(bot)

    def _add_subcommands(self, cmds):
        entries = ''
        for name, command in cmds:
            if name in command.aliases:
                # skip aliases
                continue

            entries += '**{0}{1} :**   {2}\n'.format(self.clean_prefix, name, command.short_doc)
        return entries

    def paginate(self, value):
        """
        To paginate a string into a list of strings under
        'lim' characters to meet discord.Embed field value
        hard limits. Currently not used until testing has
        been done on whether it is needed.

        :param value: string to paginate
        :return list: list of strings under 'lim' chars
        """
        lim = 1024
        spl = value.split('\n')
        ret = []
        string = ''
        for i in spl:
            if len(string) + len(i) < (lim - 1):
                string = '{0}{1}\n'.format(string, i)
            else:
                ret.append(string)
                string = '{0}'.format(i)
        else:
            ret.append(string)
        return ret

    async def format(self, ctx, command):
        """Formats command for output.

        Returns a dict used to build embed"""

        # All default values for embed dict
        self.command = command
        self.context = ctx
        emb = {
            'embed': {
                'title': '',
                'description': '',
            },
            'footer': {
                'text': self.get_ending_note()
            },
            'fields': []
        }

        description = command.description if not self.is_cog() else inspect.getdoc(command)
        if not description == '':
            description = '*{0}*'.format(description)

        if description:
            # <description> portion
            emb['embed']['description'] = description

        if isinstance(command, discord.ext.commands.core.Command):
            # <signature portion>
            emb['embed']['title'] = 'Syntax: {0}'.format(self.get_command_signature())

            # <long doc> section
            if command.help:
                name = '__{0}__'.format(command.help.split('\n\n')[0])
                name_length = len(name) - 4
                value = command.help[name_length:].replace('[p]', self.clean_prefix)
                if value == '':
                    value = '{0}{1}'.format(self.clean_prefix, command.name)
                field = {
                    'name': name,
                    'value': value,
                    'inline': False
                }
                emb['fields'].append(field)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                return emb

        # Review if needed. Inspect errors if not used because it doesn't match inher
        max_width = self.max_name_size

        def category(tup):
            # Turn get cog (Category) name from cog/list tuples
            cog = tup[1].cog_name
            return '**{}:**'.format(cog) if cog is not None else '\u200bNo Category:'

        # Get subcommands for bot or category
        filtered = await self.filter_command_list()

        if self.is_bot():
            # Get list of non-hidden commands for bot.
            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                field = {
                    'inline': False
                }
                commands = sorted(commands)
                if len(commands) > 0:
                    field['name'] = category
                    field['value'] = self._add_subcommands(commands)  # May need paginated
                    emb['fields'].append(field)

        else:
            # Get list of commands for category
            filtered = sorted(filtered)
            if filtered:
                field = {
                    'name': 'Commands:',
                    'value': self._add_subcommands(filtered),  # May need paginated
                    'inline': False
                }

                emb['fields'].append(field)

        return emb

    async def format_help_for(self, ctx, command_or_bot):
        """Formats the help page and handles the actual heavy lifting of how  ### WTF HAPPENED?
        the help command looks like. To change the behaviour, override the
        :meth:`~.HelpFormatter.format` method.

        Parameters
        -----------
        context: :class:`.Context`
            The context of the invoked help command.
        command_or_bot: :class:`.Command` or :class:`.Bot`
            The bot or command that we are getting the help of.

        Returns
        --------
        list
            A paginated output of the help command.
        """
        self.context = ctx
        self.command = command_or_bot
        return await self.format(ctx, command_or_bot)

    def simple_embed(self, title=None, description=None, color=None, author=None):
        # Shortcut
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=self.bot.formatter.get_ending_note())
        if author:
            embed.set_author(**author)
        return embed

    def cmd_not_found(self, cmd, color=0):
        # Shortcut for a shortcut. Sue me
        embed = self.simple_embed(title=self.bot.command_not_found.format(cmd),
                                  description='Commands are case sensitive. Please check your spelling and try again',
                                  color=color, author=self.author)
        return embed

    @commands.command(name='help', hidden=True)
    async def help(self, ctx, *cmds: str):
        """Shows help documentation.

        [p]**help**: Shows the help manual.

        [p]**help** command: Show help for a command

        [p]**help** Category: Show commands and description for a category"""
        bot = self.bot
        if isinstance(ctx.channel, discord.DMChannel):
            color = 0
            name = bot.user.name
        else:
            color = ctx.me.color
            name = ctx.guild.me.display_name if not '' else bot.user.name
        self.author = {
                'name': '{0} Help Manual'.format(name),
                'icon_url': bot.user.avatar_url_as(format='png')
            }
        destination = ctx.message.author if bot.pm_help else ctx.message.channel

        def repl(obj):
            return _mentions_transforms.get(obj.group(0), '')

        # help by itself just lists our own commands.
        if len(cmds) == 0:
            emb_dict = await bot.formatter.format_help_for(ctx, bot)

        elif len(cmds) == 1:
            # try to see if it is a cog name
            name = _mention_pattern.sub(repl, cmds[0])
            command = None
            if name in bot.cogs:
                command = bot.cogs[name]
            else:
                command = bot.all_commands.get(name)
                if command is None:
                    await destination.send(embed=self.cmd_not_found(name, color))
                    return

            emb_dict = await bot.formatter.format_help_for(ctx, command)
        else:
            name = _mention_pattern.sub(repl, cmds[0])
            command = bot.all_commands.get(name)
            if command is None:
                await destination.send(embed=self.cmd_not_found(name, color))
                return

            for key in cmds[1:]:
                try:
                    key = _mention_pattern.sub(repl, key)
                    command = command.all_commands.get(key)
                    if command is None:
                        await destination.send(embed=self.cmd_not_found(key, color))
                        return
                except AttributeError:
                    await destination.send(embed=self.simple_embed(title=
                                           'Command "{0.name}" has no subcommands.'.format(command), color=color,
                                                                   author=self.author))
                    return

            emb_dict = await bot.formatter.format_help_for(ctx, command)

        embed = discord.Embed(color=color, **emb_dict['embed'])
        embed.set_author(**self.author)
        for field in emb_dict['fields']:
            embed.add_field(**field)
        embed.set_footer(**emb_dict['footer'])
        await destination.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
