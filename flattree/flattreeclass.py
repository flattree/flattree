from collections.abc import Mapping
from . import SEPARATOR
from .common import fix_key, delete_empty
from .flatten import FlatTreeData, flatten, unflatten


class FlatTree(FlatTreeData):
    """Main tool to work with nested dictionaries using "flat" keys.

    Flat keys are path-like strings with level keys joined by "sep":
    e.g. 'level01.level02.level03.leaf' where dot is a sep.

    Attributes:
        *trees: flat or regular trees to merge for initialization
        root (str): flat key prefix (puts tree in branch rather than root)
        separator (str): symbol to separate components of a flat key
        aliases: dictionary in a form of {alias: flat_key}.
            Aliases are flat key shortcuts.
        default: value to return if key is not found during dictionary access
             when raise_key_error is not set
        raise_key_error: if True, raise exception rather than return ``default``

    """
    def __init__(self, *trees, root=None, separator=SEPARATOR,
                 aliases=None, default=None, raise_key_error=False):
        self.in_init = True
        self.aliases = {}
        self.default = default
        self.raise_key_error = raise_key_error
        if not len(trees):
            data = {fix_key(root, separator=separator): None}
        else:
            data = flatten(*trees, root=root, separator=separator)
        super().__init__(data, separator=separator)
        if isinstance(aliases, Mapping):
            self.update_aliases(aliases)
        self.in_init = False

    def update_aliases(self, aliases):
        """Updates alias dictionary, removing aliases with None value
        Args:
            aliases: new aliases

        """
        new_aliases = {}
        for key, value in aliases.items():
            if value is None:
                new_aliases[key] = None
            else:
                new_aliases[key] = fix_key(value, separator=self.sep)
        self.aliases.update(new_aliases)
        delete_empty(self.aliases)

    def __missing__(self, key):
        if self.raise_key_error:
            raise KeyError(key)
        else:
            return self.get(key, self.default)

    def get(self, key, default=None):
        clean_key = fix_key(key, separator=self.sep)
        alias_key = self.aliases.get(key, None)
        value = default
        if clean_key == '':
            value = self.tree
        else:
            if alias_key is not None:
                try_roots = (clean_key, alias_key)
            else:
                try_roots = (clean_key, )
            for root in try_roots:
                try:
                    value = unflatten(self.data,
                                      root=root,
                                      separator=self.sep,
                                      raise_key_error=True)
                    break
                except KeyError:
                    continue
        return value

    def __delitem__(self, key):
        work_key = self.aliases.get(key, fix_key(key, separator=self.sep))
        if not work_key == '':
            if work_key in self.data:
                super().__delitem__(work_key)
            else:
                for datakey in [k for k in self.data]:
                    if datakey.startswith(work_key+self.sep):
                        super().__delitem__(datakey)
            return self

    def __setitem__(self, name, value):
        if self.in_init:
            super().__setitem__(name, value)
        else:
            work_key = self.aliases.get(name, fix_key(name, separator=self.sep))
            if work_key in self.data and not isinstance(value, Mapping):
                super().__setitem__(work_key, value)
            else:
                self.__delitem__(work_key)
                tree_before = self.tree
                self.data = {work_key: value}
                self.data = flatten(self.tree, tree_before,
                                    root='', separator=self.sep)
