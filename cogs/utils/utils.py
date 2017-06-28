import redis


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Bool transforms will be performed on these redis commands
    command_list = ['HGET', 'HGETALL', 'GET', 'LRANGE']

    def parse_response(self, connection, command_name, **options):
        ret = super().parse_response(connection, command_name, **options)
        if command_name in self.command_list:
            return bool_transform(ret)
        else:
            return ret
