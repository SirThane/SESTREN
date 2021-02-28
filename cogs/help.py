# -*- coding: utf-8 -*-

"""
A reconstruction of my help.py built for the new
discord.py's help.py instead of v1.0.0a-'s formatter.py

All help messages will be embed and pretty.

Whereas previously, I used formatter.py's code and shimmed
Embeds in, this time, it is simpler to override the methods
help.py exposes for subclassing. It's less stolen code, but
still follows the same logic as the builtin help command

Cog class name becomes Category name.
Docstr on cog class becomes Category description.
Docstr on command definition becomes command summary and usage.
Use [p] in command docstr for bot prefix.

See [p]help on Line 135 for example.

await bot.help_command.send_help_for(ctx, command, [msg]) to
send help page for command. Optionally pass a string as
third arg to add a more descriptive message to help page.
e.g. send_help_for(ctx, ctx.command, "Missing required arguments")

2/20/2021
Rewritten to now use Danny's experimental ``MenuPages`` class
for pagination. Abstracted multiple methods, majorly reduced
the number of lines, and completely removed the implementation
of manually checking for reactions and storing timed sessions.

discord.py v1.6.0

SirThane#1780
"""

# Lib
from typing import Dict, List, Optional, Tuple, Union

# Site
from discord.abc import Messageable
from discord.channel import DMChannel
from discord.colour import Colour
from discord.embeds import Embed
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import Command, Group
from discord.ext.commands.help import HelpCommand as BaseHelpCommand
from discord.ext.menus import button, MenuPages, ListPageSource, Last
from discord.message import Message

try:
    # My subclassing of Bot
    from utils.classes import Bot
except ImportError:
    # So I can provide this cog to others
    from discord.ext.commands.bot import Bot


ZWSP = u'\u200b'


class HelpPageSource(ListPageSource):

    def __init__(self, entries: List[Embed]):
        super().__init__(entries, per_page=1)

    async def format_page(self, menu: MenuPages, page):
        offset = menu.current_page * self.per_page
        return self.entries[offset]


class HelpMenuPages(MenuPages):

    # For reference of the default buttons included in lib
    BUILTIN_BUTTONS = {
        "first":    b"\xE2\x8F\xAE\xEF\xB8\x8F".decode("utf8"),  # ⏮️:track_previous:
        "previous": b"\xE2\x97\x80\xEF\xB8\x8F".decode("utf8"),  # ◀️:arrow_backward:
        "next":     b"\xE2\x96\xB6\xEF\xB8\x8F".decode("utf8"),  # ▶️:arrow_forward:
        "last":     b"\xE2\x8F\xAD\xEF\xB8\x8F".decode("utf8"),  # ⏭️:track_next:
        "stop":     b"\xE2\x8F\xB9\xEF\xB8\x8F".decode("utf8")   # ⏹️:stop_button:
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove the stop button and add the red X with the same function
        self.remove_button(self.BUILTIN_BUTTONS["stop"])

    @button("❌", position=Last(2))
    async def stop_pages(self, payload):
        self.stop()


class HelpCommand(BaseHelpCommand):
    """The implementation of the help command.

    This implementation formats the help pages into embeds instead of
    markdown command blocks. I like pretty things. Sue me.

    This inherits from :class:discord.ext.commands.help.`HelpCommand`.
    It extends it with the following attributes.

    Attributes
    ------------
    dm_help: :class:`bool`
        A bool that indicates if the help command should DM the user instead of
        sending it to the channel it received it from. If the boolean is set to
        ``True``, then all help output is DM'd. If ``False``, the help output
        is sent to context
        Defaults to ``False``.
    field_limit: :class:`int`
        The number of fields that will be added to a help page before it is
        automatically paginated
        Defaults to ``6``.
    time_limit: :class:`int`
        Expiry time limit on help command output in seconds. Will automatically
        delete message and remove from active help sessions dict when time limit
        is reached
        Defaults to ``120``
    help: :class:`str`
        A string that will be set as the help command's help manual entry page
    """

    def __init__(self, **options):
        self.dm_help = options.pop('dm_help', False)

        # Number of fields before a help command's output gets paginated
        self.field_limit = options.pop("field_limit", 6)

        # Seconds to wait before help manual times out
        self.time_limit = options.pop("time_limit", 120)

        # Command.short_doc splits Command.help, not raw docstr from inspect, so this sets help_command.short_doc too
        self.help = options.pop("help", "Shows Help Manual Documentation\n\n"
                                        ""
                                        "`[p]help` for all commands\n"
                                        "`[p]help command` for a command's help page\n"
                                        "`[p]help Category` for all commands in a Category")

        # Used for send_help_for
        # Stored as class attribute instead of passing as parameter so we don't need to override command_callback
        self._title = None

        super().__init__(command_attrs={"help": self.help}, **options)

    """ ################################################
         Special attributes for command/bot information
        ################################################ """

    @property
    def bot(self) -> Bot:
        return self.ctx.bot

    @property
    def ctx(self) -> Context:
        """Short name for context I use more commonly in signatures"""
        return self.context

    @ctx.setter
    def ctx(self, context: Context):
        self.context = context

    @property
    def is_dm(self) -> bool:
        """Returns True if command or caller is from DMs"""
        return isinstance(self.ctx.channel, DMChannel)

    """ ############################################
         Attributes for constructing the base embed
        ############################################ """

    def em_base(self) -> Embed:
        """Prepare a basic embed that will be common to all outputs"""
        em = Embed(title=self.title, description="", color=self.color)
        em.set_author(**self.author)
        em.set_footer(text=self.footer)

        return em

    @property
    def title(self) -> Optional[str]:
        """An optional message that can be sent to send_help_for that adds to Embed title"""
        return self._title

    @title.setter
    def title(self, msg: Optional[str]):
        self._title = msg

    @property
    def author(self) -> Dict[str, str]:
        """Returns an author dict for constructing Embed"""

        # No display names in DMs
        if self.is_dm:
            name = self.bot.user.name
        else:
            name = self.ctx.guild.me.display_name

        author = {
            'name': f'{name} Help Manual',
            'icon_url': self.avatar
        }
        return author

    @property
    def avatar(self) -> str:
        """Returns web URL for bot account's avatar"""
        return self.bot.user.avatar_url_as(format='png')

    @property
    def color(self) -> Colour:
        """Returns current role colour of bot if from Guild, or default Embed colour if DM"""
        if self.is_dm:
            return Embed.Empty
        else:
            return self.ctx.guild.me.colour

    @property
    def footer(self) -> str:
        """Returns help command's ending note"""
        command_name = self.invoked_with if self.invoked_with else "help"
        return f"Type {self.clean_prefix}{command_name} command for more info on a command.\n" \
               f"You can also type {self.clean_prefix}{command_name} Category for more info on a category."

    @property
    def dest(self) -> Messageable:
        """Returns the destination Help output will be sent to"""
        if self.dm_help or self.is_dm:
            return self.ctx.author
        else:
            return self.ctx.channel

    """ ############
         Pagination
        ############ """

    async def send(self, em: Embed, fields: List[Dict[str, Union[str, bool]]]) -> None:
        """The callback that the message and sets the help
        command session for a user

        This is the bit that actually puts the message in
        the channel"""

        ems = list()

        # Split list of fields into a list of smaller lists with __len__ of self.field_limit
        for group in [list(fields[i:self.field_limit + i]) for i in range(0, len(fields), self.field_limit)]:

            # Make a copy of the base Embed for each group of fields
            page = em.copy()

            for field in group:
                page.add_field(**field)

            ems.append(page)

        for i, em in enumerate(ems):
            em.set_author(
                name=f"{em.author.name}  ({i + 1}/{len(ems)})",
                url=em.author.url,
                icon_url=em.author.icon_url
            )

        msg = await self.dest.send(embed=ems[0])

        menu = HelpMenuPages(
            source=HelpPageSource(ems),
            delete_message_after=True,
            clear_reactions_after=True,
            message=msg,
            timeout=self.time_limit
        )

        await menu.start(self.ctx)

    @staticmethod
    def paginate_field(name: str, value: str, extend: str) -> List[Dict[str, Union[str, bool]]]:
        """Takes parameters for an Embed field and returns a
        list of field dicts with values under 1024 characters

        :param name:
            :class:`str` field header
        :param value:
            :class:`str` field value
        :param extend:
            :class:`str` header for additional fields
        """

        fields = list()

        # Account for large cogs and split them into separate fields
        field = {
            "name": name,
            "value": "",
            "inline": False
        }

        # Don't want to slice mid line, so split on new lines
        # Knock on wood, no lines over 1024 TODO
        values = value.split("\n")

        for value in values:

            # Embed field value maximum length, less 1 for line return
            if len(value) + len(field["value"]) < 1023:
                field["value"] += f"\n{value}"
            else:

                # Add field to fields list and start a new one
                fields.append(field)
                field = {
                    "name": extend,
                    "value": value,
                    "inline": False
                }

        else:
            # Add the field if one field or add the last field if multiple
            fields.append(field)

        return fields

    """ ################
         Error handling
        ################ """

    async def send_error_message(self, error: str):
        """Called in help callback, so we need to override it to use new Embeds"""
        await self.send_help_for(self.ctx, self.ctx.command, error)

    """ ########################
         Formatting and sending
        ######################## """

    async def prepare_help_command(self, ctx: Context, cmd: Optional[str] = None):
        """Method called before command processing"""
        self.ctx = ctx

    async def send_help_for(
            self,
            ctx: Context,
            cmd: Union[Cog, Command, Group] = None,
            msg: Optional[str] = None
    ) -> Message:
        """Can be accessed as a method of bot.help_command to send help pages
        from outside of [p]help. Useful in on_command_error event. Be careful
        as this method is not the builtin default help_command and will be
        removed if the cog is unloaded"""

        # Set the title of the embed so custom messages can be added in
        self.title = msg

        # Good thing Cog, Command, and Group all have .qualified_name
        # If no cmd, Bot help page will be sent
        msg = await self.command_callback(ctx, command=cmd.qualified_name if cmd else None)

        # Remove title, so it doesn't carry over
        # Would move ot prepare_help_command, but it is called in command_callback
        self.title = None

        return msg

    def format_doc(self, item: Union[Bot, Cog, Command, Group]) -> Tuple[str, str]:
        """Get and format the help information to be added to embeds

        Change this method to changed markdown and formatting"""

        # Only added to Embed body, so description is fine
        # Fields will be headed by Cogs and filled by Commands
        if isinstance(item, Bot):
            if item.description:
                desc = item.description.replace("[p]", self.clean_prefix)

                # Maximum embed body description length
                if len(desc) > 2043:
                    desc = f"{desc[:2043]}..."

                # Don't need bot name since it's in the Embed Author
                return f"*{desc}*", ""
            else:

                # Need to have something in the body and v1.2.4 doesn't respect ZWSPs anymore, so repeat bot name
                return f"*{item.user.name}*", ""

        # Get Cog name and description if it has one
        # Both are added to the body
        elif isinstance(item, Cog):
            if item.description:
                # "CogName", "*Description: $command for use*"
                return item.qualified_name, f"*{item.description.replace('[p]', self.clean_prefix)}*"
            else:
                # "CogName", ""
                return item.qualified_name, ""

        # Groups and Commands are treated the same
        elif isinstance(item, Command) or isinstance(item, Group):

            # Command.brief can optionally be set at definition
            # Use it if it's available, otherwise, use the automatic short_doc using first line from docstr
            brief = item.brief if item.brief else item.short_doc

            # Command.help is automatically set from full docstr on definition
            desc = item.help

            # .help will be None if no docstr
            if desc:
                desc = desc.replace(brief, "").strip("\n").replace("[p]", self.clean_prefix)

            # If no .help or if .help same as .short_doc
            if not desc:
                desc = "No help manual page exists for this command."

            # If no .brief or no .short_doc, change to .name after checking .help in case name is mentioned in .help
            if not brief:
                brief = item.name

            return brief, desc

        else:
            raise TypeError(f"{str(item)}: {item.__class__.__name__} not a subclass of Bot, Cog, Command, or Group.")

    def format_cmds_list(self, cmds: List[Union[Command, Group]]) -> str:
        """Formats and paginates the list of a cog's commands

        Change this method to change markdown and how commands
        listed for Bot, Cog, and Group. Will be paginated later
        in """

        lines = list()

        for cmd in cmds:

            # Get and format the one line entry for cmd
            brief, _ = self.format_doc(cmd)
            lines.append(f"**{self.clean_prefix}{cmd.qualified_name}**   {brief}")

        return "\n".join(lines)

    """ #####################################################################################
         Callbacks for help command for arguments Bot [no argument], Cog, Command, and Group
        ##################################################################################### """

    async def send_bot_help(self, mapping: Dict[Union[Cog, None], List[Command]], msg: str = None) -> None:
        """Prepares help for help command with no argument"""

        em = self.em_base()
        fields = list()

        # Set Embed body description as cog's docstr
        em.description, _ = self.format_doc(self.bot)

        for cog, cmds in mapping.items():

            # Get list of unhidden, commands in cog that user passes checks for
            cmds = await self.filter_commands(cmds, sort=True)

            # If cog doesn't have any commands user can run, skip it
            if not cmds:
                continue

            # Get header (Category name) for Embed field
            category = cog.qualified_name if cog else "No Category"

            # Add fields for commands list
            formatted_cmds = self.format_cmds_list(cmds)
            paginated_fields = self.paginate_field(f"**__{category}__**", formatted_cmds, f"**__{category} (Cont.)__**")
            fields.extend(paginated_fields)

        await self.send(em, fields)

    async def send_cog_help(self, cog: Cog) -> None:
        """Prepares help when argument is a Cog"""

        em = self.em_base()
        fields = list()

        # Add Cog name and description if it has one
        em.description = "**__{}__**\n{}".format(*self.format_doc(cog))

        # Get list of un-hidden, enabled commands that the invoker passes the checks to run
        cmds = await self.filter_commands(cog.get_commands(), sort=True)

        # Add fields for commands list
        if cmds:
            str_cmds = self.format_cmds_list(cmds)
            paginated_fields = self.paginate_field(f"**__Commands__**", str_cmds, f"**__Commands (Cont.)__**")
            fields.extend(paginated_fields)

        await self.send(em, fields)

    async def send_group_help(self, group: Group) -> None:
        """Prepares help when argument is a command Group"""

        em = self.em_base()
        fields = list()

        # Get command usage
        if group.usage:
            usage = f"`Syntax: {self.clean_prefix}{group.qualified_name} {group.usage}`"
        else:
            usage = f"`Syntax: {self.get_command_signature(group)}`"

        # Add command name and usage to Embed body description
        em.description = f"**__{group.qualified_name}__**\n{usage}"

        # Add fields for command help manual
        brief, doc = self.format_doc(group)
        paginated_fields = self.paginate_field(f"__{brief}__", doc, f"(Cont.)")
        fields.extend(paginated_fields)

        # Get subcommands if any and add them
        cmds = await self.filter_commands(group.commands, sort=True)
        if cmds:
            str_cmds = self.format_cmds_list(cmds)
            paginated_fields = self.paginate_field(f"**__Subcommands__**", str_cmds, f"**__Subcommands (Cont.)__**")
            fields.extend(paginated_fields)

        await self.send(em, fields)

    async def send_command_help(self, cmd: Command) -> None:
        """Prepares help when argument is a Command"""

        em = self.em_base()
        fields = list()

        # Get command usage
        if cmd.usage:
            usage = f"`Syntax: {self.clean_prefix}{cmd.qualified_name} {cmd.usage}`"
        else:
            usage = f"`Syntax: {self.get_command_signature(cmd)}`"

        # Add command name and usage to Embed body description
        em.description = f"**__{cmd.qualified_name}__**\n{usage}"

        # Add fields for command help manual
        brief, doc = self.format_doc(cmd)
        paginated_fields = self.paginate_field(f"__{brief}__", doc, f"(Cont.)")
        fields.extend(paginated_fields)

        await self.send(em, fields)


class Help(Cog):
    """Formats and Provides Help Manual Documentation for Commands

    `[p]help` will show all available commands
    `[p]help Category` will show all commands belonging to a category
    `[p]help command` will show a command's help page and all available subcommands if any"""

    def __init__(self, bot: Bot):
        self.bot = bot

        # Store the currently loaded implementation of HelpCommand
        self._original_help_command = bot.help_command

        # Replace currently loaded help_command with ours and set this cog as cog so it's not uncategorized
        bot.help_command = HelpCommand(dm_help=self.bot.dm_help, field_limit=6, time_limit=120)
        bot.help_command.cog = self

        # Make send_help_for available as a coroutine method of Bot
        bot.send_help_for = bot.help_command.send_help_for

    def cog_unload(self):
        """House-cleaning when cog is unloaded

        Restore state of help_command to before cog was loaded"""

        # Use :param cog property setter to remove Cog from help_command
        self.bot.help_command.cog = None

        # Restore the help_command that was loaded before cog load
        self.bot.help_command = self._original_help_command

        async def send_help_for(ctx: Context, cmd: Union[Cog, Command, Group] = None, msg: str = None) -> None:
            """Dummy placeholder to alert and prevent accidental usage after removal"""
            raise AttributeError(f"Coroutine `Bot.send_help_for` is not available after Help cog is unloaded.\n"
                                 f"Params: ctx: {ctx}\n"
                                 f"        cmd: {cmd}\n"
                                 f"        msg: {msg}")

        # Replace send_help_for with a dummy coro that raises AttributeError if
        # it is attempted to be used after cog is unloaded
        self.bot.send_help_for = send_help_for
        self.bot.help_command.send_help_for = send_help_for


def setup(bot: Bot):
    """Help"""
    bot.add_cog(Help(bot))
