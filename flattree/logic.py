from collections.abc import Mapping, MutableSequence
from collections import ChainMap, deque
import re

_BS = '\\'
SELR = ('.', _BS, '\u23A1', '\u23A6')
#SELR = ('.', '\\', '[', ']')


def genleaves(*trees, prepend=None, selr=SELR):
    """Generator used internally to merge trees and decompose them into leaves

    Args:
        trees: nested dictionaries to merge
        prepend: list of key components to prefix resulting flatkey strings
        selr: tuple of Separator, Escape, Left Bracket, Right Bracket symbols

    Yields:
        tuples (flatkey, scalar leaf value)
        Example: ('my.branch.x', 0)

    """
    if not trees:
        trees = [None]
    sep, esc, lb, rb = selr
    if prepend is None:
        prepend = []
        prefix = None
    else:  # escape separator
        prefix = sep.join(x.replace(sep, esc + sep) for x in prepend)
    lead_tree = trees[0]
    if isinstance(lead_tree, MutableSequence):  # a list
        for i, el in enumerate(lead_tree):
            yield from genleaves(el,
                                 prepend=prepend + [lb + str(i) + rb],
                                 selr=selr)
    elif not isinstance(lead_tree, Mapping):  # not a dictionary, assume scalar
        yield prefix, lead_tree
    else:
        realtrees = [tree for tree in trees if isinstance(tree, Mapping)]
        for lead in ChainMap(*realtrees):
            subtrees = [tree[lead] for tree in realtrees if lead in tree]
            yield from genleaves(*subtrees, prepend=prepend + [lead], selr=selr)


def flatkey_to_keylist(flatkey, selr=SELR):
    """Converts flatkey to a list of key components, extracts list indices

    Components that look like '[1000]' where a number is found between
        the Left Bracket and the Right Bracket are converted to integers,
        int("1000") in this example.

    Args:
        flatkey (str): flatkey string
        selr: tuple of Separator, Escape, Left Bracket, Right Bracket symbols

    Returns:
        list: key components, int if

    """
    if flatkey is None:
        return []
    sep, esc, lb, rb = selr
    if not sep:
        return [flatkey]
    flatk = flatkey
    if esc:
        flatk = flatk.replace('\r', '')
        flatk = flatk.replace(esc + sep, '\r')
    keylist = flatk.split(sep)
    result = []
    for key in keylist:
        if esc:
            key = key.replace('\r', sep)
        if key.startswith(lb) and key.endswith(rb):
            try:
                key = int(key[len(lb):-len(rb)])
            except (IndexError, ValueError):
                pass
        result.append(key)
    return result


def keylist_to_flatkey(keylist, selr=SELR):
    """Converts list of key components to a flatkey string

    Integer key components are considered list indices and get converted.

    Args:
        keylist (list): list of key components
        selr: tuple of Separator, Escape, Left Bracket, Right Bracket symbols

    Returns:
        str: flatkey string

    """
    if keylist is None:
        return None
    sep, esc, lb, rb = selr
    keylist = [lb + str(k) + rb if isinstance(k, int) else k for k in keylist]
    if esc and sep:
        esep = esc + sep
        keylist = [k.replace(sep, esep) for k in keylist if isinstance(k, str)]
    return sep.join(keylist) if keylist else None


def tree_with_lists(tree):
    if not isinstance(tree, Mapping):
        return tree
    sparse = {k: v for k, v in tree.items() if isinstance(k, int)}
    if sparse:
        result = [None] * (max(sparse.keys()) + 1)
        for k in sparse:
            result[k] = sparse[k]
    else:
        result = {k:tree_with_lists(tree[k]) for k in tree}
    return result


def unflatten(flatdata, top=None, selr=SELR,
              default=None, raise_key_error=False):
    """Restores nested dictionaries from a flat tree starting with a branch.

    Args:
        flatdata (dict): dictionary of values indexed by flatkeys
        top: list of key components that constitute a branch to unflatten
            (None for the whole tree)
        selr (tuple): Separator, Escape, Left Bracket, Right Bracket symbols
        default: default value
            Returned in case no branch is found and raise_key_error is False.
        raise_key_error (bool): if True, raise exception rather than
            return the default value in case no branch is found

    Returns:
        Tree or leaf value or default.

    """
    # First check if we can hit the leaf
    topfk = keylist_to_flatkey(top, selr=selr)
    if topfk in flatdata:
        return flatdata[topfk]
    # flabra: flat branch, a flat subtree of a flat tree, let's build it
    sep, esc, lb, rb = selr
    if topfk is None:
        flabra = flatdata  # the whole tree
    else:
        flabra = {key[len(topfk + sep):]: value
                  for key, value in flatdata.items()
                  if key.startswith(topfk + sep)}
    # Check if flat branch is not empty, otherwise return default of raise error
    if not flabra:
        if raise_key_error:
            raise KeyError(topfk)
        else:
            return default
    # Now build a tree
    tree = {}
    for flatkey, value in flabra.items():
        keylist = flatkey_to_keylist(flatkey, selr=selr)
        branch = tree
        for n, key in enumerate(keylist, start=1 - len(keylist)):
            try:
                if n:
                    branch = branch[key]
                else:
                    branch[key] = value
            except KeyError:
                branch[key] = {}
                branch = branch[key]
    return tree_with_lists(tree)
