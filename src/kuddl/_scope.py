from ._yaml_wrappers import YamlDict


class NullScope:
    def __init__(self, args, root):
        self._root = root
        self._args = args

    @property
    def root(self):
        return self._root

    @property
    def args(self):
        return self._args

    def _freeze(self, _call_site=True):
        return {"root": self._root, "args": self._args}

    def __getitem__(self, item):
        return getattr(self, item)

    def __getattr__(self, attr):
        return self.__getattribute__(attr)

    def _add(self, obj):
        return Scope(this=obj, up=self)


class Scope:
    def __init__(self, this, up):
        self._this = this
        self._up = up
        self._hasvars = isinstance(this, (YamlDict,))

    @property
    def this(self):
        return self._this

    @property
    def up(self):
        return self._up

    def __getitem__(self, item):
        if self._hasvars:
            return getattr(self, item)
        else:
            return self._this[item]

    def __getattr__(self, attr):
        if self._hasvars:
            if attr in self._this:
                return self._this[attr]
            else:
                return getattr(self.up, attr)
        else:
            return getattr(self.up, attr)

    def _freeze(self, _call_site=True):
        f = self.up._freeze(_call_site=False)
        if self._hasvars:
            f = {**f, **self.this}
        if _call_site:
            f = {**f, "this": self.this, "up": self.up}
        return f

    def _add(self, obj):
        return Scope(this=obj, up=self)
