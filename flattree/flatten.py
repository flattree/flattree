import collections
from .common import SEPARATOR, is_dict, fix_key


def flatten(*trees, root=None, separator=SEPARATOR):
    """Merges trees and creates dictionary of leaves indexed by flat keys.

    Flat keys are path-like strings with level keys joined by `separator`:
    e.g. 'level01.level02.level03.leaf'.

    Args:
        *trees: nested dictionaries to merge
        root (str): prefix for the keys
        separator (str): symbol to separate levels in a flat key

    Examples:
        >>> print(flatten({'x': {'a': 0}}, {'x': {'b': 1}}))
        {'x.a': 0, 'x.b': 1}

    Returns:
        Dictionary of leaves indexed by flat keys.
    """
    if len(trees) == 0:
        return None
    data = {}
    prefix = fix_key(root)
    if not is_dict(trees[0]):
        data = {prefix: trees[0]}
    else:
        # onlytrees = (d.tree if isinstance(d, FlatTree) else d for d in trees)
        onlytrees = trees
        realtrees = [tree for tree in onlytrees if is_dict(tree)]
        for lead in collections.ChainMap(*realtrees):
            values = [tree[lead] for tree in realtrees if lead in tree]
            subtree = flatten(*values, root=separator.join((prefix, lead)))
            data.update(subtree)
    return data
