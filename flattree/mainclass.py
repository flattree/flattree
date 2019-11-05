from collections.abc import Mapping
from .core import FlatTreeData, flatten, unflatten
from . import SEP, ESC


class FlatTree(FlatTreeData):
    """Main tool to work with nested dictionaries using "flat" keys.

    Flat keys are path-like strings with key components joined by "sep":
    e.g. 'level01.level02.level03.leaf' where dot is a sep.

    Attributes:
        *trees: flat or regular trees to merge for initialization
        root (str): flat key prefix (puts tree in branch rather than root)
        sep (str): symbol to use when joining key components
        esc (str): symbol to escape sep in key components
        aliases: dictionary in a form of {alias: flat_key}.
            Aliases are flat key shortcuts.
        default: value to return if key is not found during dictionary access
             when raise_key_error is not set
        raise_key_error: if True, raise exception rather than return ``default``

    """

    def __init__(self, *trees, root=None, sep=None, esc=None,
                 aliases=None, default=None, raise_key_error=False):
        self.sep = SEP if sep is None else str(sep)
        self.esc = ESC if esc is None else str(esc)
        self.aliases = {}
        self.default = default
        self.raise_key_error = raise_key_error
        self.data = flatten(*trees, root=root, sep=self.sep, esc=self.esc)
        if aliases:
            self.update_aliases(aliases)

    def update_aliases(self, aliases):
        """Updates alias dictionary, removing aliases with None value
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
        alias_key = self.aliases.get(key, None)
        value = default
        if key is None:
            value = self.tree
        else:
            if alias_key is not None:
                try_roots = (key, alias_key)
            else:
                try_roots = (key,)
            for root in try_roots:
                try:
                    value = unflatten(self.data,
                                      root=root,
                                      sep=self.sep,
                                      esc=self.esc,
                                      raise_key_error=True)
                    break
                except KeyError:
                    continue
        return value

    def __delitem__(self, key):
        work_key = self.aliases.get(key, key)
        if work_key in self.data:
            super().__delitem__(work_key)
        else:
            for datakey in [k for k in self.data]:
                if datakey.startswith(work_key + self.sep):
                    super().__delitem__(datakey)

    def __setitem__(self, name, value):
        work_key = self.aliases.get(name, name)
        if work_key in self.data and not isinstance(value, Mapping):
            super().__setitem__(work_key, value)
        else:
            self.__delitem__(work_key)
            tree_before = self.tree
            self.data = {work_key: value}
            self.data = flatten(self.tree, tree_before,
                                root=None, sep=self.sep, esc=self.esc)
