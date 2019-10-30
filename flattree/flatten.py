import collections
from . import SEPARATOR
from .common import is_dict, clean_key



def flatten(*trees, root=None, separator=SEPARATOR):
    """Merges trees and creates dictionary of leaves indexed by flat keys.

    Flat keys are path-like strings with level keys joined by ``separator``:
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
    prefix = clean_key(root)
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


def unflatten(flatdata, root=None, separator=SEPARATOR, on_key_error=None):
    """Restores nested dictionaries from flat tree starting with root.

        Calling ``unflatten(flatten(x))`` should return ``x``
        (keys may be sorted differently if ``x`` is a dictionary).

        Args:
            flatdata: dictionary of values indexed by "flat" keys
            root (str): branch to restore ('' for the whole tree)
            separator (str): symbol that separates levels in a flat key
            on_key_error: object or BaseException subclass.
                In case no leaf or branch can be found for the root,
                raise on_error if possible, otherwise return on_error.

        Returns:
            Dictionary or leaf value.

        """
    root = clean_key(root)
    if root in flatdata:
        return flatdata[root]
    if root == '':
        prefix = ''
        stems = {k: k for k in flatdata}
    else:
        prefix = root + separator
        plen = len(prefix)
        stems = {k: k[plen:] for k in flatdata if k.startswith(prefix)}
    if stems == {}:
        if (type(on_key_error) == type(BaseException) and
                issubclass(on_key_error, BaseException)):
            raise on_key_error
        else:
            tree = on_key_error
    else:
        tree = {}
        leads = set()
        for leaf, stick in stems.items():
            if stick.count(separator) == 0:
                tree[stick] = flatdata[leaf]
            else:
                leads.add(stick.split(separator)[0])
        for lead in leads:
            newroot = prefix + lead
            if newroot in flatdata:
                tree[lead] = flatdata[newroot]
            else:
                tree[lead] = unflatten(flatdata, newroot)
    return tree