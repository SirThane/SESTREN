"""Utility functions and classes.
"""

import redis


def paginate(value):
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


def bool_str(arg):
    if arg == 'True':
        return True
    elif arg == 'False':
        return False
    else:
        return arg


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


class StrictRedis(redis.StrictRedis):
    """Turns 'True' and 'False' values returns
    in redis to bool values"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Bool transforms will be performed on these redis commands
    command_list = ['HGET', 'HGETALL', 'GET', 'LRANGE']

    def parse_response(self, connection, command_name, **options):
        ret = super().parse_response(connection, command_name, **options)
        # ret = eval(compile(ret, '<string>', 'eval'))
        if command_name in self.command_list:
            return bool_transform(ret)
        else:
            return ret
