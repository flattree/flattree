from collections.abc import Mapping, MutableSequence
from collections import ChainMap, deque
import re

_BS = '\\'
SELR = ('.', _BS, '\u23A1', '\u23A6')


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
    sep, esc, lb, rb = selr
    if prepend is None:
        prepend = []
        prefix = None
    else:  # escape separator
        prefix = sep.join(x.replace(sep, esc + sep) for x in prepend)
    lead_tree = trees[0]
    if isinstance(lead_tree, MutableSequence):  # a list
        for i, el in enumerate(lead_tree):
            prelist = prepend.copy()
            if not prelist:
                prelist = ['']
            prelist[-1] = prelist[-1] + lb + str(i) + rb
            yield from genleaves(el, prepend=prelist, selr=selr)
    elif not isinstance(lead_tree, Mapping):  # not a dictionary, assume scalar
        yield prefix, lead_tree
    else:
        realtrees = [tree for tree in trees if isinstance(tree, Mapping)]
        for lead in ChainMap(*realtrees):
            subtrees = [tree[lead] for tree in realtrees if lead in tree]
            yield from genleaves(*subtrees, prepend=prepend + [lead], selr=selr)


def flatkey_to_keylist(flatkey, selr=SELR):
    """Converts flatkey string to a list of key components

    Args:
        flatkey (str): flatkey string
        selr: tuple of Separator, Escape, Left Bracket, Right Bracket symbols

    Returns:
        str: "flat" key

    """
    if flatkey is None:
        return []
    sep, esc, lb, rb = selr
    if esc and sep:
        flatkey = flatkey.replace('\r', '')
        flatkey = flatkey.replace(esc + sep, '\r')
    keylist = flatkey.split(sep) if sep else [flatkey]
    return [x.replace('\r', sep) for x in keylist] if esc and sep else keylist


def unflatten(flatdata, branch=None, selr=SELR,
              default=None, raise_key_error=False):
    """Restores nested dictionaries from a flat tree starting with a branch.

    Args:
        flatdata (dict): dictionary of values indexed by flatkeys
        branch: substring of branch to restore (None for the whole tree)
        selr (tuple): Separator, Escape, Left Bracket, Right Bracket symbols
        default: default value
            Returned in case no branch is found and raise_key_error is False.
        raise_key_error (bool): if True, raise exception rather than
            return the default value in case no branch is found

    Returns:
        Tree or leaf value or default.

    """
    branch = str(branch) if branch is not None else None
    if branch in flatdata:  # we've hit the leaf
        return flatdata[branch]
    # flabra: flat branch, a flat subtree of a flat tree, let's build it
    sep, esc, lb, rb = selr
    build_list = False  # lists are legit part of trees (since v2)
    if branch is None:
        flabra = flatdata  # the whole tree
        if any(flatkey.startswith(lb) for flatkey in flabra):
            build_list = True
    else:
        flabra = {}
        for flatkey, value in flatdata.items():
            if flatkey.startswith(branch + sep):
                flabra[flatkey[len(branch)+1:]] = value
            elif flatkey.startswith(branch + lb):
                build_list = True
                flabra[flatkey[len(branch):]] = value
    # Check if flat branch is not empty, otherwise return default of raise error
    if not flabra:
        if raise_key_error:
            raise KeyError(branch)
        else:
            return default
    # Now build a tree
    if build_list:
        # first, let's build an intermediate "sparse list"
        sparse = {}
        for flatkey, value in flabra.items():
            if flatkey.startswith(lb):
                idxkey, *downkeys = flatkey_to_keylist(flatkey, selr=selr)
                try:
                    sparse[int(idxkey[1:-1])] = (downkeys, value)
                except (IndexError, ValueError):
                    pass
        if not sparse:  # all keys were discarded
            if raise_key_error:
                raise KeyError(branch)
            else:
                return default
        else:  # build real list from the sparse one
            result = [None] * (max(sparse.keys()) + 1)  # placeholder
            for i in sparse:
                downkeys, value = sparse[i]
                if downkeys:
                    result[i] = unflatten({sep.join(downkeys): value}, None,
                                          selr=SELR,
                                          default=default,
                                          raise_key_error=False)
                else:
                    result[i] = value
    else:  # build dictionary, not a list
        result = {}
        list_ptn = ("(.+[^" + _BS + esc + "])" +
                    _BS + lb + r"\d+" + _BS + rb + "$")
        re_list_ptn = re.compile(list_ptn)
        for flatkey, value in flabra.items():
            sub_branch = flatkey_to_keylist(flatkey, selr=selr)[0]
            # If sub-branch is a list element, extract list name
            ptn_match = re.match(re_list_ptn, sub_branch)
            if ptn_match:
                sub_branch = ptn_match.group(1)
            result[sub_branch] = unflatten(flabra, sub_branch, selr=SELR,
                                           default=default,
                                           raise_key_error=False)
    return result
