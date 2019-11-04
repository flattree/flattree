from collections.abc import Mapping
from collections import ChainMap

SEP = '.'
ESC = '\\'


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
        sep (str): symbol used when joining key components
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


def flatten(*trees, root=None, sep=None, esc=ESC):
    if not trees:
        return None
    sep = SEP if sep is None else str(sep)
    esc = ESC if esc is None else str(esc)
    flattree = {}
    rootlist = flatkey_to_keylist(root, sep=sep, esc=esc)
    for keylist, value in genleaves((rootlist, *trees)):
        flattree[keylist_to_flatkey(keylist, sep=sep, esc=esc)] = value
    return flattree


def unflatten(flattree, root=None, sep=None, esc=None):
    sep = SEP if sep is None else str(sep)
    esc = ESC if esc is None else str(esc)
    tree = {}
    rootlist = flatkey_to_keylist(root, sep=sep, esc=esc)
    for flatkey, value in flattree.items():
        keylist = rootlist + flatkey_to_keylist(flatkey, sep=sep, esc=esc)
        if not keylist:
            return value
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
