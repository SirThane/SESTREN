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
            'author': {
                'name': '{0.display_name} Help Manual'.format(self.bot.user),
                'icon_url': self.bot.user.avatar_url_as(format='jpeg')
            },
            'footer': {
                'text': ''
            },
            'fields': []
        }

        # we need a padding of ~80 or so

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)
        if not description == '':
            description = '*{0}*'.format(description)

        if description:
            # <description> portion
            # self._paginator.add_line(description, empty=True)
            emb['embed']['description'] = description

        if isinstance(self.command, discord.ext.commands.core.Command):
            # <signature portion>
            # signature = self.get_command_signature()
            # self._paginator.add_line(signature, empty=True)
            emb['embed']['title'] = 'Syntax: {0}'.format(self.get_command_signature())

            # <long doc> section
            if self.command.help:
                # self._paginator.add_line(self.command.help, empty=True)
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
                # self._paginator.close_page()
                # return self._paginator.pages
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
                    # self._paginator.add_line(category)

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

        # add the ending note
        emb['footer']['text'] = self.get_ending_note()
        return emb


class Help:

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')
        self.bot.formatter = HelpFormatter(bot)

    async def format_help_for(self, context, command_or_bot):
        """Formats the help page and handles the actual heavy lifting of how
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

    @commands.command(name='help', aliases=['h'])
    async def help(self, ctx, *cmds: str):
        """Shows help documentation.

        [p]**help**
        Shows the help manual.

        [p]**help** command:
        Show help for a command

        [p]**help** Category:
        Show commands and description for a category"""
        bot = self.bot
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
                    await destination.send(bot.command_not_found.format(name))
                    return

            emb_dict = await bot.formatter.format_help_for(ctx, command)
        else:
            name = _mention_pattern.sub(repl, cmds[0])
            command = bot.all_commands.get(name)
            if command is None:
                await destination.send(bot.command_not_found.format(name))
                return

            for key in cmds[1:]:
                try:
                    key = _mention_pattern.sub(repl, key)
                    command = command.all_commands.get(key)
                    if command is None:
                        await destination.send(bot.command_not_found.format(key))
                        return
                except AttributeError:
                    await destination.send(bot.command_has_no_subcommands.format(command, key))
                    return

            emb_dict = await bot.formatter.format_help_for(ctx, command)

        # if bot.pm_help is None:
        #     characters = sum(map(lambda l: len(l), emb))
        #     # modify destination based on length of pages.
        #     if characters > 1000:
        #         destination = ctx.message.author

        embed = discord.Embed(color=ctx.me.color, **emb_dict['embed'])
        if len(emb_dict['author']) > 0:
            embed.set_author(**emb_dict['author'])
        for field in emb_dict['fields']:
            embed.add_field(**field)
        embed.set_footer(**emb_dict['footer'])
        await destination.send(embed=embed)
        # await destination.send(emb['embed']['description'])

        # for page in emb:
        #     await destination.send(page)


def setup(bot):
    bot.add_cog(Help(bot))