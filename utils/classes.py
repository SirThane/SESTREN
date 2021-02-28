# -*- coding: utf-8 -*-


from __future__ import annotations

# Lib
from asyncio import CancelledError
from asyncio.tasks import sleep
from re import match
from traceback import extract_tb
from typing import Any, Dict, Generator, List, Set, Tuple, Union

# Site
from discord.appinfo import AppInfo
from discord.channel import TextChannel
from discord.colour import Colour
from discord.embeds import Embed as DiscordEmbed
from discord.errors import DiscordException, LoginFailure
from discord.ext.commands import Bot as DiscordBot
from discord.ext.commands.context import Context
from discord.ext.commands.converter import IDConverter
from discord.ext.commands.errors import BadArgument
from discord.message import Message
from discord.utils import get, find
from redis.client import StrictRedis as DefaultStrictRedis

# Local
from utils.utils import ZWSP, bool_transform, _get_from_guilds


class Embed(DiscordEmbed):

    STR_PAGE_DEPTH = {
        0: "\n",
        1: " ",
        2: ""
    }

    def copy(self):
        """Returns a shallow copy of the embed.

        Must copy the method from discord.Embed, or it would
        return a copy of the super class."""
        return Embed.from_dict(self.to_dict())

    def strip_head(self):
        """Removes all values from header elements"""
        self.title = ""
        self.description = ""
        self.set_author(name="", url="", icon_url="")
        self.set_thumbnail(url="")

    def strip_foot(self):
        """Removes all values from footer elements"""
        self.set_image(url="")
        self.set_footer(text="", icon_url="")

    """ ##################################
         Header Element Length Properties
        ################################## """

    @property
    def title_len(self) -> int:
        return len(self.title) if self.title else 0

    @property
    def description_len(self) -> int:
        return len(self.description) if self.description else 0

    @property
    def auth_name_len(self) -> int:
        return len(self.author.name) if self.author.name else 0

    @property
    def auth_url_len(self) -> int:
        return len(self.author.url) if self.author.url else 0

    @property
    def auth_icon_len(self) -> int:
        return len(self.author.icon_url) if self.author.icon_url else 0

    @property
    def thumb_len(self) -> int:
        return len(self.thumbnail.url) if self.thumbnail.url else 0

    """ ##################################
         Footer Element Length Properties
        ################################## """

    @property
    def image_len(self) -> int:
        return len(self.image.url) if self.image.url else 0

    @property
    def foot_text_len(self) -> int:
        return len(self.footer.text) if self.footer.text else 0

    @property
    def foot_icon_len(self) -> int:
        return len(self.footer.icon_url) if self.footer.icon_url else 0

    """ ###############
         Field lengths
        ############### """

    @property
    def fields_len(self) -> List[int]:
        return [len(field.name) + len(field.value) for field in self.fields]

    """ #############
         Length Sums
        ############# """

    @property
    def head_len(self) -> int:
        return sum((
            self.title_len,
            self.description_len,
            self.auth_name_len,
            self.auth_url_len,
            self.auth_icon_len,
            self.thumb_len
        ))

    @property
    def foot_len(self) -> int:
        return sum((
            self.image_len,
            self.foot_text_len,
            self.foot_icon_len
        ))

    """ ############
         Pagination
        ############ """

    @staticmethod
    def deconstruct_string(string: str, limit: int = 1000, depth: int = 0) -> List[Tuple[str, str]]:
        """Transforms a string into a list of tuples. The second element
        of each tuple will be a section of the string. The first element
        will be the breaking character that separates it from the next
        section."""

        # Prioritize line breaks, then spaces, then no delimiter
        # Without a delimiter, it will stop at `limit` characters for
        # words longer than `limit`
        delimiter = Embed.STR_PAGE_DEPTH[depth]

        if Embed.STR_PAGE_DEPTH[depth]:
            strings = [(delimiter, piece) for piece in string.split(delimiter)]
        else:
            strings = [(delimiter, piece) for piece in list(string)]

        ret = list()

        # Build a list of each component section of the original string paired
        # the the character that separated it from the next section
        for delim, string in strings:
            if len(delim) + len(string) <= limit:
                ret.append((delim, string))
            else:
                ret.extend(Embed.deconstruct_string(string, limit, depth + 1))

        return ret

    @staticmethod
    def paginate_string(string: str, limit: int = 1000) -> List[str]:
        """Deconstruct a string into section/delimiter pairs and reconstitute
        into a list of strings shorter than `limit`"""

        deconstructed_string = Embed.deconstruct_string(string, limit)

        ret = list()

        # Prepare the first element
        next_delim, page = deconstructed_string.pop(0)

        for delim, string in deconstructed_string:

            # Translate delimiters back into priorities for comparison
            # Higher order delimiters take precedence to prevent merging words
            delim_depth = {k: v for v, k in Embed.STR_PAGE_DEPTH.items()}
            if delim_depth.get(delim) > delim_depth.get(next_delim):
                next_delim = delim

            if len(page) + len(next_delim) + len(string) <= limit:
                page = next_delim.join((page, string))
                next_delim = delim

            else:
                ret.append(page)
                page = string
                next_delim = delim

        ret.append(page)
        return ret

    def paginate_fields(self, limit: int = 1000) -> None:

        fields: List[dict] = [field.copy() for field in self.to_dict().get("fields")]
        self.clear_fields()

        for field in fields:

            if len(field["value"]) <= limit:
                self.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )
                continue

            value: str = field["value"]

            if value.startswith("```") and value.endswith("```"):
                cb_wrapped: bool = True
                md: str = value.split("\n")[0].strip("```")
                value: str = value.strip("```")
                if md:
                    value: str = value.replace(f"{md}\n", "")
            else:
                cb_wrapped: bool = False
                md: str = ""

            values = self.paginate_string(value, limit)

            if cb_wrapped:
                values = [f"```{md}\n{value}\n```" for value in values]

            for i, value in enumerate(values):
                self.add_field(
                    name=f"{field['name']}{' (Cont.)' if i else ''}",
                    value=value,
                    inline=field["inline"]
                )

    def split(self) -> List[Embed]:

        self.paginate_fields(limit=1010)

        if self.head_len + self.foot_len + sum(self.fields_len) < 6000:
            return [self]

        pages = list()
        page: Embed = self.copy()

        fields = [field.copy() for field in self.to_dict().get("fields", None)]

        page.clear_fields()
        page.strip_foot()

        for field in fields:

            field_len = len(field["name"]) + len(field["value"])

            if all((
                page.head_len + len(page.fields_len) + field_len < 6000,
                len(page.fields) <= 25
            )):
                page.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )

            else:
                pages.append(page)

                page: Embed = self.copy()
                page.strip_head()
                page.clear_fields()
                page.strip_foot()

                page.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"]
                )

        if page.head_len + len(page.fields_len) + self.foot_len < 6000:
            page.set_footer(
                text=self.footer.text,
                icon_url=self.footer.icon_url
            )
            pages.append(page)

        else:
            pages.append(page)

            page = self.copy()
            page.strip_head()
            page.clear_fields()

            pages.append(page)

        return pages


class ErrorLog:

    def __init__(self, bot, channel: Union[int, str, TextChannel]):
        self.bot = bot
        if isinstance(channel, int):
            channel = self.bot.get_channel(channel)
        elif isinstance(channel, str):
            channel = self.bot.get_channel(int(channel))
        if isinstance(channel, TextChannel):
            self.channel = channel
        else:
            self.channel = None

    async def send(self, error: Union[Exception, DiscordException], ctx: Context = None, event: str = None) -> Message:
        if not self.channel:
            raise AttributeError("ErrorLog channel not set")
        em = await self.em_tb(error, ctx, event)
        for i, page in enumerate(em.split()):
            if i:
                await sleep(0.1)
            return await self.channel.send(embed=em)

    @staticmethod
    async def em_tb(error: Union[Exception, DiscordException], ctx: Context = None, event: str = None) -> Embed:
        if ctx:
            prefix = await ctx.bot.get_prefix(ctx.message)
            title = f"In {prefix}{ctx.command.qualified_name}"
            description = f"**{error.__class__.__name__}**: {error}"
        else:
            title = f"Exception ignored in event `{event}`" if event else None
            description = f"**{type(error).__name__}**: {str(error)}"

        stack = extract_tb(error.__traceback__)
        tb_fields = [
            {
                "name": f"{ZWSP}\n__{fn}__",
                "value": f"Line `{ln}` in `{func}`:\n```py\n{txt}\n```",
                "inline": False
            } for fn, ln, func, txt in stack
        ]

        em = Embed(color=Colour.red(), title=title, description=f"{description}")

        for field in tb_fields:
            em.add_field(**field)

        return em


class Bot(DiscordBot):

    def __init__(self, **kwargs):

        # Redis db instance made available to cogs
        self.db: SubRedis = kwargs.pop("db", None)

        # Name of bot stored in Bot instance
        # Used as key name for db
        self.APP_NAME: str = kwargs.pop("app_name", None)

        # Legacy compatibility for Help command
        self.dm_help: bool = kwargs.pop('dm_help', False) or kwargs.pop('pm_help', False)
        self.pm_help: bool = self.dm_help

        # Used by timer cog
        self.secs: int = 0

        # Declaring first. This will not be able to get set until login
        self.app_info: AppInfo = kwargs.get("app_info", None)

        # Get the channel ready for errorlog
        # Bot.get_channel method not available until on_ready
        self.errorlog_channel: int = kwargs.pop("errorlog", None)
        self.errorlog: ErrorLog = kwargs.get("errorlog", None)

        # Added by help.bak.py
        # Supress IDE errors
        self.send_help_for = None

        # Changed signature from arg to kwarg so I can splat the hgetall from db in main.py
        command_prefix: str = kwargs.pop("command_prefix", "!")

        super().__init__(command_prefix, **kwargs)

    def run(self, **kwargs):
        # Changed signature from arg to kwarg so I can splat the hgetall from db in main.py
        token = kwargs.pop("token", None)
        if not token:
            raise LoginFailure("No or improper token passed")
        super().run(token, **kwargs)

    async def _run_event(self, coro, event_name: str, *args, **kwargs):
        # Override built-in event handler so we can capture errors raised
        try:
            await coro(*args, **kwargs)
        except CancelledError:
            pass
        except Exception as error:
            try:
                await self.on_error(event_name, *args, error_captured=error, **kwargs)
            except CancelledError:
                pass

    async def on_error(self, event_name, *args, **kwargs):
        """Error handler for Exceptions raised in events"""

        # Try to get Exception that was raised
        error = kwargs.pop("error_captured")

        # If the Exception raised is successfully captured, use ErrorLog
        if error:
            await self.errorlog.send(error, event=event_name)

        # Otherwise, use default handler
        else:
            await super().on_error(event_method=event_name, *args, **kwargs)


class StrictRedis(DefaultStrictRedis):
    """Turns 'True' and 'False' values returns
    in redis to bool values"""

    # Bool transforms will be performed on these redis commands
    command_list = ['HGET', 'HGETALL', 'GET', 'LRANGE']

    def parse_response(self, connection, command_name, **options):
        ret = super().parse_response(connection, command_name, **options)
        # ret = eval(compile(ret, '<string>', 'eval'))
        if command_name in self.command_list:
            return bool_transform(ret)
        else:
            return ret


class SubRedis:

    def __init__(self, db: Union[StrictRedis, SubRedis], basekey: str):

        if isinstance(db, SubRedis):
            self.root = db.root
            self.basekey = f"{db.basekey}:{basekey}"

        else:
            self.root = db
            self.basekey = basekey

    """ ###############
         Managing Keys
        ############### """

    def exists(self, *names: str) -> int:
        """Returns the number of ``names`` that exist"""
        names = [f"{self.basekey}:{name}" for name in names]
        return self.root.exists(*names)

    def delete(self, *names: str) -> Any:
        """Delete one or more keys specified by ``names``"""
        names = [f"{self.basekey}:{name}" for name in names]
        return self.root.delete(*names)

    """ ###########
         Iterators
        ########### """

    def scan_iter(self, match: str = None, count: int = None, _type: str = None) -> Generator[str, str, None]:
        """
        Make an iterator using the SCAN command so that the client doesn't
        need to remember the cursor position.

        ``pattern`` allows for filtering the keys by pattern

        ``count`` allows for hint the minimum number of returns
        """
        if not match == "*":
            match = f":{match}"
        for item in self.root.scan_iter(match=f"{self.basekey}{match}", count=count, _type=_type):
            yield item.replace(f"{self.basekey}:", "")

    """ ###############
         Simple Values
        ############### """

    def set(self, name: str, value: str, ex: int = None, px: int = None, nx: bool = False, xx: bool = False) -> Any:
        """
        Set the value at key ``name`` to ``value``

        ``ex`` sets an expire flag on key ``name`` for ``ex`` seconds.

        ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.

        ``nx`` if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist.

        ``xx`` if set to True, set the value at key ``name`` to ``value`` only
            if it already exists.
        """
        return self.root.set(f"{self.basekey}:{name}", value, ex, px, nx, xx)

    def get(self, name: str) -> str:
        """Return the value at key ``name``, or None if the key doesn't exist"""
        return self.root.get(f"{self.basekey}:{name}")

    """ ######
         Sets
        ###### """

    def scard(self, name: str) -> int:
        """Return the number of elements in set ``name``"""
        return self.root.scard(f"{self.basekey}:{name}")

    def sismember(self, name: str, value: str) -> bool:
        """Return a boolean indicating if ``value`` is a member of set ``name``"""
        return self.root.sismember(f"{self.basekey}:{name}", value)

    def smembers(self, names: str) -> Set[str]:
        """Return all members of the set ``name``"""
        return self.root.smembers(f"{self.basekey}:{names}")

    def sadd(self, name: str, *values: str) -> Any:
        """Add ``value(s)`` to set ``name``"""
        return self.root.sadd(f"{self.basekey}:{name}", *values)

    def srem(self, name: str, *values: str) -> Any:
        """Remove ``values`` from set ``name``"""
        return self.root.srem(f"{self.basekey}:{name}", *values)

    """ #######
         Lists
        ####### """

    def lrange(self, name: str, start: int, end: int) -> List[str]:
        """
        Return a slice of the list ``name`` between
        position ``start`` and ``end``

        ``start`` and ``end`` can be negative numbers just like
        Python slicing notation
        """
        return self.root.lrange(f"{self.basekey}:{name}", start, end)

    def lpush(self, name: str, *values: str) -> Any:
        """Push ``values`` onto the head of the list ``name``"""
        return self.root.lpush(f"{self.basekey}:{name}", *values)

    def lrem(self, name: str, count: int, value: str) -> Any:
        """
        Remove the first ``count`` occurrences of elements equal to ``value``
        from the list stored at ``name``.

        The count argument influences the operation in the following ways:
            count > 0: Remove elements equal to value moving from head to tail.
            count < 0: Remove elements equal to value moving from tail to head.
            count = 0: Remove all elements equal to value.
        """
        return self.root.lrem(f"{self.basekey}:{name}", count, value)

    """ #############################
         Hashes (Dict-like Mappings)
        ############################# """

    def hget(self, name: str, key: str) -> str:
        """Return the value of ``key`` within the hash ``name``"""
        return self.root.hget(f"{self.basekey}:{name}", key)

    def hkeys(self, name: str) -> List[str]:
        """Return the list of keys within hash ``name``"""
        return self.root.hkeys(f"{self.basekey}:{name}")

    def hvals(self, name: str) -> List[str]:
        """Return the list of values within hash ``name``"""
        return self.root.hvals(f"{self.basekey}:{name}")

    def hgetall(self, name: str) -> Dict[str, Any]:
        """Return a Python dict of the hash's name/value pairs"""
        return self.root.hgetall(f"{self.basekey}:{name}")

    def hset(self, name: str, key: str, value: str) -> Any:
        """
        Set ``key`` to ``value`` within hash ``name``
        Returns 1 if HSET created a new field, otherwise 0
        """
        return self.root.hset(f"{self.basekey}:{name}", key, value)

    def hmset(self, name: str, mapping: dict) -> Any:
        """
        Set key to value within hash ``name`` for each corresponding
        key and value from the ``mapping`` dict.
        """
        return self.root.hmset(f"{self.basekey}:{name}", mapping)

    def hdel(self, name: str, *keys):
        """Delete ``keys`` from hash ``name``"""
        return self.root.hdel(name, *keys)


class Paginator:

    def __init__(
            self,
            page_limit: int = 1000,
            trunc_limit: int = 2000,
    ):
        self.page_limit = page_limit
        self.trunc_limit = trunc_limit
        self._pages = None

    @property
    def pages(self):
        return self._pages

    def set_trunc_limit(self, limit: int = 2000):
        self.trunc_limit = limit

    def set_page_limit(self, limit: int = 1000):
        self.page_limit = limit

    def paginate(self, value: str) -> List[str]:
        """
        To paginate a string into a list of strings under
        `self.page_limit` characters. Total len of strings
        will not exceed `self.trunc_limit`.
        :param value: string to paginate
        :return list: list of strings under 'page_limit' chars
        """
        spl = str(value).split('\n')
        ret = list()
        page = ''
        total = 0

        for i in spl:
            if total + len(page) >= self.trunc_limit:
                ret.append(page[:self.trunc_limit - total])
                break

            if (len(page) + len(i)) < self.page_limit:
                page += f'\n{i}'
                continue

            else:
                if page:
                    total += len(page)
                    ret.append(page)

                if len(i) > (self.page_limit - 1):
                    tmp = i
                    while len(tmp) > (self.page_limit - 1):
                        if total + len(tmp) < self.trunc_limit:
                            total += len(tmp[:self.page_limit])
                            ret.append(tmp[:self.page_limit])
                            tmp = tmp[self.page_limit:]
                        else:
                            ret.append(tmp[:self.trunc_limit - total])
                            break
                    else:
                        page = tmp
                else:
                    page = i
        else:
            ret.append(page)

        self._pages = ret
        return self.pages


class GlobalTextChannelConverter(IDConverter):
    """Converts to a :class:`~discord.TextChannel`.

    Copy of discord.ext.commands.converters.TextChannelConverter,
    Modified to always search global cache.

    The lookup strategy is as follows (in order):

    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name
    """
    async def convert(self, ctx: Context, argument: str) -> TextChannel:
        bot = ctx.bot

        search = self._get_id_match(argument) or match(r'<#([0-9]+)>$', argument)

        if match is None:
            # not a mention
            if ctx.guild:
                result = get(ctx.guild.text_channels, name=argument)
            else:
                def check(c):
                    return isinstance(c, TextChannel) and c.name == argument
                result = find(check, bot.get_all_channels())
        else:
            channel_id = int(search.group(1))
            if ctx.guild:
                result = ctx.guild.get_channel(channel_id)
            else:
                result = _get_from_guilds(bot, 'get_channel', channel_id)

        if not isinstance(result, TextChannel):
            raise BadArgument('Channel "{}" not found.'.format(argument))

        return result
