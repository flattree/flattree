from collections.abc import Mapping
from collections import UserDict
from . import SEP, ESC
from .logic import (genleaves, unflatten, desparse,
                    keylist_to_flatkey, flatkey_to_keylist)


class FlatTree(UserDict):
    """Main tool to work with nested dictionaries using "flat" keys.

    Flat keys are path-like strings with key components joined by "sep":
    e.g. 'level01.level02.level03.leaf' where dot is a sep.

    Attributes:
        *trees: flat or regular trees, merged initialization
        root (str): flat key prefix (puts tree in branch rather than root)
        sep (str): symbol to use when joining key components
        esc (str): symbol to escape sep in key components
        aliases: dictionary in a form of {alias: flat_key}.
            Aliases are flat key shortcuts.
        default: value to return if key is not found during dictionary access
             when raise_key_error is not set
        raise_key_error: if True, raise exception rather than return ``default``

    """
    def __init__(self, *trees, root=None, sep=SEP, esc=ESC,
                 aliases=None, default=None, raise_key_error=False):
        self._item_logic = False
        super().__init__(self.flatten(*trees, root=root, sep=sep, esc=esc))
        self.sep = SEP if sep is None else str(sep)
        self.esc = ESC if esc is None else str(esc)
        self.aliases = {}
        self.default = default
        self.raise_key_error = raise_key_error
        if aliases:
            self.update_aliases(aliases)
        self._item_logic = True

    @classmethod
    def flatten(cls, *trees, root=None, sep=SEP, esc=ESC):
        """Merges nested dictionaries into a flat key dictionary."""
        noflat = [d.tree if isinstance(d, cls) else d for d in trees]
        pre = flatkey_to_keylist(root, sep=sep, esc=esc)
        return dict(genleaves(*noflat, pre=pre, sep=sep, esc=esc))

    def unflatten(self, root=None, default=None, raise_key_error=False):
        uf = unflatten(self.data, root=root, sep=self.sep, esc=self.esc,
                       default=default, raise_key_error=raise_key_error)
        return desparse(uf, reindex=True)

    @property
    def tree(self):
        """Regular tree dynamically recovered from the flat tree."""
        return self.unflatten()

    @tree.setter
    def tree(self, value):
        if isinstance(value, type(self)):
            self.data = value.data.copy()
        else:
            leaf_gen = genleaves(value, pre=None, sep=self.sep, esc=self.esc)
            self.data = dict(leaf_gen)

    def update_aliases(self, aliases):
        """Updates alias dictionary, removes aliases if value is None

        Args:
            aliases: new aliases

        """
        if isinstance(aliases, Mapping):
            for key, value in aliases.items():
                if value is None:
                    if key in self.aliases:
                        del self.aliases[key]
                else:
                    self.aliases[key] = value

    def __missing__(self, key):
        if self.raise_key_error:
            raise KeyError(key)
        else:
            return self.get(key, self.default)

    def get(self, key, default=None):
        if key is None:
            value = self.tree
        else:
            alias_key = self.aliases.get(key, None)
            value = default
            if alias_key is not None:
                try_roots = (str(key), alias_key)
            else:
                try_roots = (str(key),)
            for root in try_roots:
                try:
                    value = self.unflatten(root=root, raise_key_error=True)
                    break
                except KeyError:
                    continue
        return value

    def __delitem__(self, key):
        work_key = self.aliases.get(key, str(key))
        if work_key in self.data:
            super().__delitem__(work_key)
        else:
            for datakey in [k for k in self.data]:  # avoid mutating  keys
                if (isinstance(datakey, str)
                        and datakey.startswith(work_key + self.sep)):
                    super().__delitem__(datakey)

    def __setitem__(self, name, value):
        if self._item_logic:
            work_key = self.aliases.get(name, name)
            if (work_key in self.data
                    and not (isinstance(value, Mapping) and value)):
                super().__setitem__(work_key, value)
            else:
                self.__delitem__(work_key)
                tree_before = self.tree
                self.data = {work_key: value}
                self.data = self.flatten(self.tree, tree_before, root=None,
                                         sep=self.sep, esc=self.esc)
        else:
            super().__setitem__(name, value)
