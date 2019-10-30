from collections.abc import Mapping


SEPARATOR = '.'


def is_dict(x):
    return x and isinstance(x, Mapping)


def fix_key(x, separator=SEPARATOR):
    if x is None:
        key = ''
    else:
        key = str(x).strip(separator)
    return key
