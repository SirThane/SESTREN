"""Overrides the built-in help formatter.

All help messages will be embed and pretty.

Most of the code stolen from
discord.ext.commands.formatter.py and
converted into embeds instead of codeblocks.

discord.py 1.0.0a"""

import discord
from discord.ext import commands
from discord.ext.commands import formatter, core
import re
import inspect
import itertools


_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}


_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))


class HelpFormatter(formatter.HelpFormatter):

    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        self.bot.formatter = self
        super().__init__(*args, **kwargs)

    def _add_subcommands_to_page(self, max_width, cmds):
        entries = ''
        for name, command in cmds:
            if name in command.aliases:
                # skip aliases
                continue

            entries += '{0}**{1} :**   {2}\n'.format(self.clean_prefix, name, command.short_doc)
        return entries
            # shortened = self.shorten(entry)
            # self._paginator.add_line(shortened)

    def paginate(self, value):
        spl = value.split('\n')
        ret = []
        string = ''
        for i in spl:
            if len(string) + len(i) < 1023:
                string = '{0}{1}\n'.format(string, i)
            else:
                ret.append(string)
                string = '{0}'.format(i)
        else:
            ret.append(string)
        return ret

    async def format(self):
        """Handles the actual behaviour involved with formatting.

        To change the behaviour, this method should be overridden.

        Returns
        --------
        list
            A paginated output of the help command.
        """
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

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)
        if not description == '':
            description = '*{0}*'.format(description)

        if description:
            # <description> portion
            emb['embed']['description'] = description

        if isinstance(self.command, discord.ext.commands.core.Command):
            # <signature portion>
            emb['embed']['title'] = 'Syntax: {0}'.format(self.get_command_signature())

            # <long doc> section
            if self.command.help:
                name = '__{0}__'.format(self.command.help.split('\n\n')[0])
                name_length = len(name) - 4
                value = self.command.help[name_length:].replace('[p]', self.clean_prefix)
                if value == '':
                    value = '{0}{1}'.format(self.clean_prefix, self.command.name)
                field = {
                    'name': name,
                    'value': value,
                    'inline': False
                }
                emb['fields'].append(field)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                return emb

        max_width = self.max_name_size

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return '**{}:**'.format(cog) if cog is not None else '\u200bNo Category:'

        filtered = await self.filter_command_list()
        if self.is_bot():
            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                field = {
                    'inline': False
                }
                commands = sorted(commands)
                if len(commands) > 0:
                    field['name'] = category
                    field['value'] = self._add_subcommands_to_page(max_width, commands)
                    emb['fields'].append(field)

        else:
            filtered = sorted(filtered)
            if filtered:
                field = {
                    'name': 'Commands:',
                    'value': self._add_subcommands_to_page(max_width, filtered),
                    'inline': False
                }

                emb['fields'].append(field)

        return emb


class Help:

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')
        self.bot.formatter = HelpFormatter(bot)

    async def format_help_for(self, context, command_or_bot):  ### TYPEERROR: FORMAT TAKES 1 POS ARG BUT GIVEN 3
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
        self.context = context
        self.command = command_or_bot
        return await self.bot.formatter.format(context, self.command)

    def simple_embed(self, title=None, description=None, color=0, author=None):
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=self.bot.formatter.get_ending_note())
        if author:
            embed.set_author(**author)
        return embed

    def cmd_not_found(self, cmd, color=0):
        embed = self.simple_embed(title=self.bot.command_not_found.format(cmd),
                                  description='Commands are case sensitive. Please check your spelling and try again',
                                  color=color, author=self.author)
        return embed

    @commands.command(name='help')
    async def help(self, ctx, *cmds: str):
        """Shows help documentation.

        [p]**help**: Shows the help manual.

        [p]**help** command: Show help for a command

        [p]**help** Category: Show commands and description for a category"""
        bot = self.bot
        color = ctx.me.color
        name = ctx.guild.me.display_name if not '' else bot.user.name
        self.author = {
                'name': '{0} Help Manual'.format(name),
                'icon_url': self.bot.user.avatar_url_as(format='jpeg')
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
                    await destination.send(embed=self.cmd_not_found(name))
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
                                           'Command "{0.name}" has no subcommands.'.format(command), color=color))
                    return

            emb_dict = await bot.formatter.format_help_for(ctx, command)

        # if bot.pm_help is None:
        #     characters = sum(map(lambda l: len(l), emb))
        #     # modify destination based on length of pages.
        #     if characters > 1000:
        #         destination = ctx.message.author

        embed = discord.Embed(color=color, **emb_dict['embed'])
        # if len(emb_dict['author']) > 0:
        embed.set_author(**self.author)
        for field in emb_dict['fields']:
            embed.add_field(**field)
        embed.set_footer(**emb_dict['footer'])
        await destination.send(embed=embed)
        # await destination.send(emb['embed']['description'])

        # for page in emb:
        #     await destination.send(page)


def setup(bot):
    bot.add_cog(Help(bot))