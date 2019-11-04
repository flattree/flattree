from collections.abc import Mapping
from collections import ChainMap, UserDict
from .common import Failure


class FlatTreeData(UserDict):
    """Container for the flat tree data.

    Used as a way to tell "flattened tree" data from regular trees.
    Contains essential methods

    Attributes:
        data: dictionary of values indexed by flat keys
        separator (str): symbol to separate components of a flat key

    """
    def __init__(self, data, separator=None):
        self.sep = separator
        super().__init__(data)

    @property
    def tree(self):
        """Regular tree dynamically recovered from the flat tree.

        Returns: object representing regular tree

        """
        return unflatten(self.data, root='', separator=self.sep)

    @tree.setter
    def tree(self, value):
        self.data = flatten(value, root='', separator=self.sep)

    def update(self, other=None, **kw):
        """ Merges the ``other`` tree in.

        Other tree has priority during merge.

        Args:
            other: tree to merge into existing data
            **kw: tree in a form of key-value pairs

        """
        if len(kw):
            data = {} if not isinstance(other, Mapping) else other.copy()
            data.update(kw)
        else:
            data = other
        self.data = flatten(data, self.tree, root='', separator=self.sep)


def flatten(*trees, root=None, separator=None):
    """Merges trees and creates dictionary of leaves indexed by flat keys.

    Flat keys are path-like strings with level keys joined by "sep":
    e.g. 'level01.level02.level03.leaf' where dot is a sep.

    The tree that comes earlier in ``*trees`` has priority during merge.

    Instances of FlatTreeData (and subclasses including FlatTree) have their
    trees recovered before merge is applied.

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
    if not len(trees):
        return None
    separator = '' if separator is None else str(separator)
    data = {}
    #prefix = fix_key(root, sep=sep)
    root = '' if root is None else str(root)
    if root == '':
        prefix = ''
    else:
        if root.startswith(separator):
            root = root[len(separator):]
        prefix = root + separator
    if not isinstance(trees[0], Mapping):
        data = {root: trees[0]}
    else:
        noflat = (d.tree if isinstance(d, FlatTreeData) else d for d in trees)
        realtrees = [tree for tree in noflat if isinstance(tree, Mapping)]
        for lead in ChainMap(*realtrees):
            values = [tree[lead] for tree in realtrees if lead in tree]
            nextroot = separator + prefix + lead
            subtree = flatten(*values,
                              root=nextroot,
                              separator=separator)
            data.update(subtree)
    return data


def unflatten(flatdata, root=None, separator=None,
              default=None, raise_key_error=False):
    """Restores nested dictionaries from flat tree starting with root.

        Calling ``unflatten(flatten(x))`` should return ``x``
        (keys may be sorted differently if ``x`` is a dictionary).

        Args:
            flatdata: dictionary of values indexed by "flat" keys
            root (str): branch to restore ('' for the whole tree)
            separator (str): symbol to separate components of a flat key
            default: default value
                Returned in case no leaf or branch is found for the root,
                and raise_key_error is False.
            raise_key_error (bool): if True, raise exception rather than
                return the default value

        Returns:
            Dictionary or leaf value.

        """
    separator = '' if separator is None else str(separator)
    root = '' if root is None else str(root)
    #root = fix_key(root, sep=sep)
    if root in flatdata:
        return flatdata[root]
    if separator == '':
        if root == '':
            tree = flatdata
        else:
            n = len(root)
            rdata = {k[n:]: flatdata[k] for k in flatdata if k.startswith(root)}
            tree = Failure(root) if rdata == {} else rdata
    else:  # Let's grow a tree
        if root == '':
            prefix = ''
            stems = {k: k for k in flatdata}
        else:
            prefix = root + separator
            plen = len(prefix)
            stems = {k: k[plen:] for k in flatdata if k.startswith(prefix)}
        if stems == {}:
            tree = Failure(root)
        else:
            tree = {}
            leads = set()
            for leaf, stem in stems.items():
                if stem.count(separator) == 0:
                    tree[stem] = flatdata[leaf]
                elif stem.startswith(separator):
                    if prefix == '':
                        leads.add(separator)
                    else:
                        leads.add('')
                else:
                    leads.add(stem.split(separator)[0])
            for lead in leads:
                nextroot = prefix + lead
                if nextroot in flatdata:
                    subtree = flatdata[nextroot]
                else:
                    subtree = unflatten(flatdata, nextroot,
                                        separator=separator)
                tree[lead] = subtree
    if isinstance(tree, Failure):
        if raise_key_error:
            raise KeyError(tree.reason)
        else:
            tree = default
    return tree
