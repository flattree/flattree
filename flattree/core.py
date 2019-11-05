from collections.abc import Mapping
from collections import ChainMap, UserDict


class FlatTreeData(UserDict):
    """Container for the flat tree data.

    Used as a way to tell "flattened tree" data from regular trees.
    Contains essential methods

    Attributes:
        data: dictionary of values indexed by flat keys
        sep (str): symbol to use when joining key components
        esc (str): symbol to escape sep in key components

    """

    def __init__(self, data, sep, esc):
        self.sep = sep
        self.esc = esc
        super().__init__(data)

    @property
    def tree(self):
        """Regular tree dynamically recovered from the flat tree.

        Returns: object representing regular tree

        """
        return unflatten(self.data, root=None, sep=self.sep, esc=self.esc)

    @tree.setter
    def tree(self, value):
        self.data = flatten(value, root=None, sep=self.sep, esc=self.esc)

    def update(self, other=None, **kw):
        """ Merges the ``other`` tree in.

        Other tree has priority during merge.

        Args:
            other: tree to merge into existing data
            **kw: tree in a form of key-value pairs

        """
        if kw:
            data = {} if not isinstance(other, Mapping) else other.copy()
            data.update(kw)
        else:
            data = other
        self.data = flatten(data, self.tree,
                            root=None, sep=self.sep, esc=self.esc)


def genleaves(treetuple):
    """Generator that merges dictionaries and decomposes them into leaves

    Args:
        treetuple (tuple): starting tuple, consists of leading list of
            prepended key components and following trees (nested dictionaries).
            Example: (['my', 'branch'], {'x': 0, 'y': 1}, {'z': {'a': None}})

    Yields:
        treetuples (list of leaf key components, scalar leaf value)
        Example: (['my', 'branch', 'x'], 0)

    """
    keylist = treetuple[0]
    trees = treetuple[1:]
    if not isinstance(trees[0], Mapping):
        yield keylist, trees[0]
    else:
        realtrees = [tree for tree in trees if isinstance(tree, Mapping)]
        for lead in ChainMap(*realtrees):
            subtrees = [tree[lead] for tree in realtrees if lead in tree]
            yield from genleaves((keylist + [lead], *subtrees))


def keylist_to_flatkey(keylist, sep, esc):
    """Converts list of key components to "flat key" string

    Args:
        keylist (list): list of key components
        sep (str): symbol to use when joining key components
        esc (str): symbol to escape sep in key components

    Returns:
        str: "flat" key

    """
    if not keylist:
        return None
    if esc and sep:
        keylist = [x.replace(sep, esc + sep) for x in keylist]
    return sep.join(keylist)


def flatkey_to_keylist(flatkey, sep, esc):
    """Converts "flat key" string to list of key components

    Args:
        flatkey (str): "flat key" string
        sep (str): symbol used when joining flat key components
        esc (str): symbol to escape sep in key components

    Returns:
        str: "flat" key

    """
    if flatkey is None:
        return []
    if esc and sep:
        flatkey = flatkey.replace('\r', '')
        flatkey = flatkey.replace(esc + sep, '\r')
    keylist = flatkey.split(sep) if sep else [flatkey]
    return [x.replace('\r', sep) for x in keylist] if esc and sep else keylist


def flatten(*trees, root, sep, esc):
    """Merges trees and creates dictionary of leaves indexed by flat keys.

    Flat keys are path-like strings with key components joined by "sep".
    Example: 'level01.level02.level03.leaf' where sep == '.'.

    The tree that comes earlier in ``*trees`` has priority during merge.

    Instances of FlatTreeData (and subclasses including FlatTree) have their
    trees recovered before merge is applied.

    Args:
        *trees: nested dictionaries to merge
        root: prefix for the flat keys
        sep (str): symbol to use when joining flat key components
        esc (str): symbol to escape sep in key components

    Returns:
        Dictionary of leaves indexed by flat keys.

    """
    if not trees:
        trees = [None]
    flattree = {}
    rootlist = flatkey_to_keylist(root, sep=sep, esc=esc)
    noflat = (d.tree if isinstance(d, FlatTreeData) else d for d in trees)
    for keylist, value in genleaves((rootlist, *noflat)):
        flattree[keylist_to_flatkey(keylist, sep=sep, esc=esc)] = value
    return flattree


def unflatten(flatdata, root, sep, esc, default=None, raise_key_error=False):
    """Restores nested dictionaries from a flat tree starting with root.

    Calling ``unflatten(flatten(x))`` should return ``x``
    (keys may be sorted differently if ``x`` is a dictionary).

    Args:
        flatdata: dictionary of values indexed by "flat" keys
        root: branch to restore (None for the whole tree)
        sep (str): symbol used when joining flat key components
        esc (str): symbol to escape sep in key components
        default: default value
            Returned in case no leaf or branch is found for the root,
            and raise_key_error is False.
        raise_key_error (bool): if True, raise exception rather than
            return the default value

    Returns:
        Dictionary or leaf value or default.

    """
    if root is None:
        if None in flatdata:
            return flatdata[None]
        flatbranch = flatdata
    else:
        root = str(root)
        if root in flatdata:
            return flatdata[root]
        flatbranch = {}
        prefix = root + sep
        plen = len(prefix)
        for flatkey, value in flatdata.items():
            if flatkey.startswith(prefix):
                flatbranch[flatkey[plen:]] = value
    if not flatbranch:
        if raise_key_error:
            raise KeyError(root)
        else:
            return default
    tree = {}
    for flatkey, value in flatbranch.items():
        keylist = flatkey_to_keylist(flatkey, sep=sep, esc=esc)
        subtree = tree
        for n, key in enumerate(keylist, start=1 - len(keylist)):
            try:
                if n:
                    subtree = subtree[key]
                else:
                    subtree[key] = value
            except KeyError:
                subtree[key] = {}
                subtree = subtree[key]
    return tree

