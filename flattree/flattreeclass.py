import collections
from . import SEPARATOR
from .common import is_dict, clean_key, delete_empty
from .flatten import flatten, unflatten


class FlatTree(collections.UserDict):
    def __init__(self, *trees, root=None, aliases=None,
                 separator=SEPARATOR, default=None):
        self.separator = separator
        self.default = default
        self.aliases = {}
        if is_dict(aliases):
            self.update_aliases(aliases)
        if len(trees) == 0:
            super().__init__({clean_key(root): None})
        else:
            super().__init__(flatten(*trees, root=root, separator=separator))

    def update_aliases(self, aliases):
        new_aliases = {}
        for key, value in aliases.items():
            if value is None:
                new_aliases[key] = None
            else:
                new_aliases[key] = clean_key(value)
        self.aliases.update(new_aliases)
        delete_empty(self.aliases)

    def __missing__(self, key):
        if self.is_valid_key(key):
            cleaned_key = clean_key(key)
            for try_key in (cleaned_key, self.aliases.get(cleaned_key, None)):
                if try_key is not None:
                    try:
                        return unflatten(self.data, root=try_key,
                                         separator=self.separator,
                                         on_key_error=KeyError)
                    except KeyError:
                        pass
        return self.default

    def is_valid_key(self, key):
        if key == '':
            return True
        cleaned_key = clean_key(key)
        valid_leaf = cleaned_key in self.data
        prefix = cleaned_key + self.separator
        valid_branch = any(k.startswith(prefix) for k in self.data)
        return valid_leaf or valid_branch

    def get(self, key, default=None):
        if self.is_valid_key(key):
            return self[key]
        else:
            return default

    @property
    def tree(self):
        return unflatten(self.data)

    @tree.setter
    def tree(self, value):
        self.data = flatten(value, root='')

"""
    def __delitem__(self, key):
        if key in self.data:
            super().__delitem__(key)
        else:
            for datakey in [k for k in self.data]:
                if datakey.startswith(key):
                    super().__delitem__(datakey)
        return self

    def __setitem__(self, name, value):
        if name in self.data and not is_dict(value):
            super().__setitem__(name, value)
        else:
            prefix = _make_branch_prefix(name)
            self.__delitem__(prefix)
            current_tree = self.tree
            self.data = {name: value}
            added_tree = self.tree
            self.data = flatten(added_tree, current_tree)
"""