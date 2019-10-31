from collections.abc import Mapping
from collections import ChainMap, UserDict
from . import SEPARATOR
from .common import fix_key


class FlatTreeData(UserDict):
    def __init__(self, data, separator=None):
        self.sep = separator
        super().__init__(data)

    @property
    def tree(self):
        return unflatten(self.data, root='', separator=self.sep)

    @tree.setter
    def tree(self, value):
        self.data = flatten(value, root='', separator=self.sep)

    def update(self, other, *kw):
        self.data = flatten(other, self.tree, root='', separator=self.sep)


def flatten(*trees, root=None, separator=SEPARATOR):
    """Merges trees and creates dictionary of leaves indexed by flat keys.

    Flat keys are path-like strings with level keys joined by ``separator``:
    e.g. 'level01.level02.level03.leaf'.

    Args:
        *trees: nested dictionaries to merge
        root (str): prefix for the keys
        separator (str): symbol to separate components of a flat key

    Examples:
        >>> print(flatten({'x': {'a': 0}}, {'x': {'b': 1}}))
        {'x.a': 0, 'x.b': 1}

    Returns:
        Dictionary of leaves indexed by flat keys.

    """
    if len(trees) == 0:
        return None
    separator = '' if separator is None else str(separator)
    data = {}
    prefix = fix_key(root, separator=separator)
    if not isinstance(trees[0], Mapping):
        data = {prefix: trees[0]}
    else:
        noflat = (d.tree if isinstance(d, FlatTreeData) else d for d in trees)
        realtrees = [tree for tree in noflat if isinstance(tree, Mapping)]
        for lead in ChainMap(*realtrees):
            values = [tree[lead] for tree in realtrees if lead in tree]
            subtree = flatten(*values,
                              root=prefix+separator+lead,
                              separator=separator)
            data.update(subtree)
    return data


def unflatten(flatdata, root=None, separator=SEPARATOR,
              default=None, raise_on_key_error=False):
    """Restores nested dictionaries from flat tree starting with root.

        Calling ``unflatten(flatten(x))`` should return ``x``
        (keys may be sorted differently if ``x`` is a dictionary).

        Args:
            flatdata: dictionary of values indexed by "flat" keys
            root (str): branch to restore ('' for the whole tree)
            separator (str): symbol to separate components of a flat key
            default: default value
                Returned in case no leaf or branch is found for the root,
                and raise_on_key_error is False.
            raise_on_key_error (bool): if True, raise exception instead of
                returning default value

        Returns:
            Dictionary or leaf value.

        """
    separator = '' if separator is None else str(separator)
    root = fix_key(root, separator=separator)
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
        if raise_on_key_error:
            raise KeyError(root)
        else:
            tree = default
    else:
        tree = {}
        leads = set()
        for leaf, stem in stems.items():
            if stem.count(separator) == 0:
                tree[stem] = flatdata[leaf]
            else:
                try:
                    leads.add(stem.split(separator)[0])
                except ValueError:
                    leads.add(stem)
        for lead in leads:
            nextroot = prefix + lead
            if nextroot in flatdata:
                tree[lead] = flatdata[nextroot]
            else:
                tree[lead] = unflatten(flatdata, nextroot, separator=separator)
    return tree
