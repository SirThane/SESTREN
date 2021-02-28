"""Utility functions and classes.
"""

# Lib
import sys
from contextlib import contextmanager
from io import StringIO, BytesIO
from time import localtime, strftime
from typing import Iterable, Tuple, Union

# Site
from aiohttp.client import ClientSession

# Local


ZWSP = u'\u200b'


def _get_from_guilds(bot, getter, argument):
    """Copied from discord.ext.commands.converter to prevent
    access to protected attributes inspection error"""
    result = None
    for guild in bot.guilds:
        result = getattr(guild, getter)(argument)
        if result:
            return result
    return result


async def download_image(url: str, file_path: Union[bytes, str, BytesIO]) -> None:
    is_bytes = False
    if isinstance(file_path, str):
        fd = open(file_path, "wb")
    else:
        is_bytes = True
        fd = file_path

    try:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                while True:
                    chunk = await resp.content.read(10)
                    if not chunk:
                        break
                    fd.write(chunk)

        fd.seek(0)

    finally:
        if not is_bytes:
            fd.close()


def get_timestamp() -> str:
    return strftime("%a %b %d, %Y at %H:%M %Z", localtime())


@contextmanager
def stdoutio(file=None):
    old = sys.stdout
    if file is None:
        file = StringIO()
    sys.stdout = file
    yield file
    sys.stdout = old


def bool_str(arg):
    if arg == 'True':
        return True
    elif arg == 'False':
        return False
    else:
        return arg


def flatten(items):
    """Yield items from any nested iterable; see Reference."""
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x


def bytespop(
        b: Union[bytes, bytearray],
        q: int = 1,
        decode: str = None,
        endian: str = "little"
) -> Tuple[Union[int, str, bytearray], bytearray]:

    if isinstance(b, bytes):
        b = bytearray(b)

    ret = b[:q]

    b = b[q:]

    if decode == "utf8":
        return ret.decode("utf8"), b
    elif decode == "int":
        return int.from_bytes(ret, endian), b
    else:
        return ret, b


def bool_transform(arg):
    if isinstance(arg, str):
        return bool_str(arg)
    elif isinstance(arg, list):
        for i in range(len(arg)):
            arg[i] = bool_str(arg[i])
        return arg
    elif isinstance(arg, dict):
        for i in arg.keys():
            arg[i] = bool_str(arg[i])
        return arg
