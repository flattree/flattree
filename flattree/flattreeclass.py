from collections.abc import Mapping
from . import SEPARATOR
from .common import fix_key, delete_empty
from .flatten import FlatTreeData, flatten, unflatten


class FlatTree(FlatTreeData):
    def __init__(self, *trees, root=None, separator=SEPARATOR,
                 aliases=None, default=None, raise_on_key_error=False):
        self.in_init = True
        self.aliases = {}
        self.default = default
        self.raise_on_key_error = raise_on_key_error
        if len(trees) == 0:
            data = {fix_key(root, separator=separator): None}
        else:
            data = flatten(*trees, root=root, separator=separator)
        super().__init__(data, separator=separator)
        if isinstance(aliases, Mapping):
            self.update_aliases(aliases)
        self.in_init = False

    def update_aliases(self, aliases):
        new_aliases = {}
        for key, value in aliases.items():
            if value is None:
                new_aliases[key] = None
            else:
                new_aliases[key] = fix_key(value, separator=self.sep)
        self.aliases.update(new_aliases)
        delete_empty(self.aliases)

    def __missing__(self, key):
        if self.raise_on_key_error:
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
                                      raise_on_key_error=True)
                    break
                except KeyError:
                    continue
        return value

    @property
    def tree(self):
        return unflatten(self.data, root='', separator=self.sep)

    @tree.setter
    def tree(self, value):
        super().__init__(flatten(value, root='', separator=self.sep))

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
