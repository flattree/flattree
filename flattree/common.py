from collections.abc import Mapping
from . import SEPARATOR


def fix_key(x, separator=SEPARATOR):
    return(x)


def delete_empty(x):
    """Removes elements with None values from a dictionary.

    Args:
        x: dictionary

    Returns:
        Does not return a value. Operation is performed in place.
    """
    if isinstance(x, Mapping):
        keys = list(x.keys())
        for k in keys:
            if x[k] is None:
                del x[k]


class Failure:
    reason = ''

    def __init__(self, reason):
        self.reason = reason
