from collections.abc import Mapping
from . import SEPARATOR


def fix_key(x, separator=SEPARATOR):
    """Handles special cases of None value or erroneous leading or trailing
    separators in flat keys.

        Args:
            x (str): flat key
            separator (str): symbol to separate components of a flat key

        Returns:
            Flat key, corrected if needed

        """
    key = '' if x is None else str(x)
    if not isinstance(separator, str) or len(separator) == 0:
        return key
    else:
        if key.startswith(separator):
            key = fix_key(key[len(separator):], separator=separator)
        elif key.endswith(separator):
            key = fix_key(key[:-len(separator)], separator=separator)
    return key


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
