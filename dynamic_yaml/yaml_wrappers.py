
_unevaluated = ()


def _dict_join(head, *tail):
    """
    Joins many dictionariess into one
    
    Priority for key conflicts goes to later references.
    """
    if len(tail) == 0:
        return head
    else:
        return {**head, **_dict_join(*tail)}


class YamlDict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        values = {k: _unevaluated for k in self.keys()}
        self.__values = values  # cached values, lazily evaluated
        
    def __repr__(self):
        # force getitem to be called
        return repr({k: self[k] for k in self.keys()})

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return super().__getattribute__(key)

    def __getitem__(self, key):
        v = super().__getitem__(key)
        if isinstance(v, str):
            if self.__values[key] is _unevaluated:
                scope = _dict_join(*self.__scope)
                v = v.format(**scope, root=self.__root, this=self)
                self.__values[key] = v
            else:
                v = self.__values[key]
        return v

    def _dynamic_yaml_eval(self, root, scope):
        self.__root = root  # yaml root reference
        scope = [*scope, self]
        self.__scope = scope  # current lexical scope
        for k, v in self.items():
            if hasattr(v, '_dynamic_yaml_eval'):
                v._dynamic_yaml_eval(root, scope)


class YamlList(list):

    def __init__(self, *args, **kwargs):
        super(YamlList, self).__init__(*args, **kwargs)
        values = [_unevaluated for i in range(len(self))]
        self.__values = values  # cached values, lazily evaluated
        
    def __repr__(self):
        # force getitem to be called
        return repr([self[i] for i in range(len(self))])

    def __getitem__(self, key):
        v = super(YamlList, self).__getitem__(key)
        if isinstance(v, str):
            if self.__values[key] is _unevaluated:
                scope = _dict_join(*self.__scope)
                v = v.format(**scope, root=self.__root, this=self)
                self.__values[key] = v
            else:
                v = self.__values[key]
        return v

    def _dynamic_yaml_eval(self, root, scope):
        self.__root = root  # yaml root reference
        scope = [*scope]
        self.__scope = scope  # current lexical scope
        for v in self:
            if hasattr(v, '_dynamic_yaml_eval'):
                v._dynamic_yaml_eval(self.__root, self.__scope)
