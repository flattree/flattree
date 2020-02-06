from collections.abc import Mapping, MutableSequence
from collections import ChainMap
from . import SEP, ESC


def keylist_to_flatkey(keylist, sep=SEP, esc=ESC):
    """Converts list of key components to a flatkey string

    Integer key components are considered list indices and get converted.

    Args:
        keylist (list): list of key components
        sep (str): symbol to use when joining flat key components
        esc (str): symbol to escape sep in key components

    Returns:
        str: flatkey string

    """
    if keylist is None:
        return None
    if esc and sep:
        esep = esc + sep
        keylist = [str(k).replace(sep, esep) for k in keylist]
    return sep.join(str(k) for k in keylist) if keylist else None


def flatkey_to_keylist(flatkey, sep=SEP, esc=ESC):
    """Converts flatkey to a list of key components, extracts list indices

    Components that look like integers, e.g. '1000' get converted to integers,
        int('1000') in this example.

    Args:
        flatkey (str): flatkey string
        sep (str): symbol to use when joining flat key components
        esc (str): symbol to escape sep in key components

    Returns:
        list: key components, int if

    """
    if flatkey is None:
        return []
    else:
        flatkey = str(flatkey)
    if not sep:
        return [flatkey]
    if esc:
        flatkey = flatkey.replace('\r', '')
        flatkey = flatkey.replace(esc + sep, '\r')
    result = []
    for key in flatkey.split(sep):
        if esc:
            key = key.replace('\r', sep)
        try:
            result.append(int(key))
        except ValueError:
            result.append(key)
    return result


def list_merger_list0(*lists):
    """Picks leading list, discards everything else"""
    return lists[0]


def genleaves(*trees, pre=None, sep=SEP, esc=ESC,
              idxbase=0, list_merger=list_merger_list0):
    """Generator used internally to merge trees and decompose them into leaves

    Args:
        trees: nested dictionaries to merge
        pre: list of key components to prepend to resulting flatkey strings
        sep (str): symbol to use when joining flat key components
        esc (str): symbol to escape sep in key components
        idxbase (int): number at which list indices would start
        list_merger: function called on trees when leading tree is a list

    Yields:
        tuples (flatkey, scalar leaf value)
        Example: ('my.branch.x', 0)

    """
    if not trees:
        trees = [None]
    if pre is None:
        pre = []
    lead_tree = trees[0]
    if isinstance(lead_tree, MutableSequence):  # a list, let's merge
        merged_lists = list_merger(*trees)
        if merged_lists:
            for i, el in enumerate(lead_tree):
                yield from genleaves(el,
                                     pre=pre + [str(idxbase + i)],
                                     sep=sep, esc=esc, idxbase=idxbase)
        else:
            yield keylist_to_flatkey(pre, sep=sep, esc=esc), merged_lists
    elif not (isinstance(lead_tree, Mapping) and lead_tree):  # no drill-down
        yield keylist_to_flatkey(pre, sep=sep, esc=esc), lead_tree
    else:
        realtrees = [tree for tree in trees if isinstance(tree, Mapping)]
        for lead in ChainMap(*realtrees):
            subtrees = [tree[lead] for tree in realtrees if lead in tree]
            yield from genleaves(*subtrees,
                                 pre=pre + [lead],
                                 sep=sep, esc=esc, idxbase=idxbase)


def unflatten(flatdata, root=None, sep=SEP, esc=ESC,
              default=None, raise_key_error=False):
    """Restores nested dictionaries from a flat tree starting with a branch.

    Args:
        flatdata (dict): dictionary of values indexed by flatkeys
        root: branch to restore (None for the whole tree)
        sep (str): symbol to use when joining flat key components
        esc (str): symbol to escape sep in key components
        default: default value
            Returned in case no branch is found and raise_key_error is False.
        raise_key_error (bool): if True, raise exception rather than
            return the default value in case no branch is found

    Returns:
        Tree or leaf value or default.

    """
    # First check if we can hit the leaf
    if root in flatdata:
        return flatdata[root]
    # flabra: flat branch, a flat subtree of a flat tree, let's build it
    if root is None:
        flabra = flatdata  # the whole tree
    else:
        flabra = {key[len(root + sep):]: value
                  for key, value in flatdata.items()
                  if isinstance(key, str) and key.startswith(root + sep)}
    # Check if flat branch is not empty, otherwise return default of raise error
    if not flabra:
        if raise_key_error:
            raise KeyError(root)
        else:
            return default
    # Now build a tree
    tree = {}
    for flatkey, value in flabra.items():
        keylist = flatkey_to_keylist(flatkey, sep=sep, esc=esc)
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
    return tree


def desparse(tree, na=None, reindex=True):
    """Converts branch(es) with integer keys into lists within a dictionary.

    Dictionary with (all) integer keys acts as a sparse list with only non-void
        values actually stored. This function would convert sparse list into
        the regular one.

    Examples:

        {1: 'one', 3: 'three'} -> ['one', 'three']  # if reindex
        {1: 'one', 3: 'three'} -> [na, 'one', na, 'three']  # if not reindex

    Args:
        tree (dict): dictionary
        na: value to fill in gaps
        reindex (bool): if True, keep compact but change non-consecutive indices

    Returns:
        dict or list

    """
    if not (isinstance(tree, Mapping) and tree):
        return tree
    try:
        keys = list(tree.keys())
        if reindex:
            keys.sort(key=int)
            result = [desparse(tree[k], na=na, reindex=reindex) for k in keys]
        else:
            result = [na] * (max(keys) + 1)  # placeholder list
            for k in tree:
                result[k] = desparse(tree[k], na=na, reindex=reindex)
    except (TypeError, ValueError, IndexError):  # some key was not numeric
        result = {k: desparse(tree[k], na=na, reindex=reindex) for k in tree}
    return result
