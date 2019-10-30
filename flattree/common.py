from collections.abc import Mapping
from . import SEPARATOR


def is_dict(x):
    """Checks if argument is a dictionary
    Args:
        x: object to check

    Returns:
        True if x is a dictionary, False otherwise
    """
    return x and isinstance(x, Mapping)


def clean_key(x, separator=SEPARATOR):
    """Handles special cases of None value or erroneous leading or trailing
    separators in flattree keys.

        Args:
            x (str): flat key

        Returns:
            Flat key, corrected if needed
        """
    if x is None:
        key = ''
    else:
        key = str(x).strip(separator)
    return key


def delete_empty(x):
    """Remove None values from a dictionary.

    Args:
        x: dictionary

    Returns:
        Does not return a value. Operation is performed in place.
    """
    if is_dict(x):
        keys = list(x.keys())
        for k in keys:
            if x[k] is None:
                del x[k]
