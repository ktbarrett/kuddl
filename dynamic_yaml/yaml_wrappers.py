
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

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return super().__getattribute__(key)

    def _dynamic_yaml_eval(self, root, stack):
        stack = stack + [self]
        for k, v in self.items():
            if hasattr(v, '_dynamic_yaml_eval'):
                self[k] = v._dynamic_yaml_eval(root, stack)
            elif isinstance(v, str):
                env = _dict_join(*stack, {'root': root, 'this': self})
                self[k] = v.format(**env)
        return self


class YamlList(list):

    def _dynamic_yaml_eval(self, root, stack):
        for i, v in enumerate(self):
            if hasattr(v, '_dynamic_yaml_eval'):
                self[i] = v._dynamic_yaml_eval(root, stack)
            elif isinstance(v, str):
                env = _dict_join(*stack, {'root': root, 'this': self})
                self[i] = v.format(**env)
        return self


class YamlEval(str):

    def _dynamic_yaml_eval(self, root, stack):
        env = _dict_join(globals(), *stack, {'root': root})
        code_str = self.format(**env)
        return eval(code_str, env, {})


class YamlBlockEval(str):

    def _dynamic_yaml_eval(self, root, stack):
        env = _dict_join(globals(), *stack, {'root': root})
        code_str = self.format(**env)
        func_str = '\n\t'.join(["def _tmp():"] + code_str.split('\n'))
        loc = {}
        exec(func_str, env, loc)
        return loc["_tmp"]()


class YamlImport(str):

    def _dynamic_yaml_eval(self, root, stack):
        env = _dict_join(*stack, {'root': root})
        import_str = self.format(**env)
        spl = import_str.split(":")
        if len(spl) == 1:
            name, = spl
            return __import__(name, globals(), {})
        elif len(spl) == 2:
            name, item = spl
            return getattr(__import__(name, globals(), {}), item)
        else:
            raise TypeError(f"Malformed import specifier: {import_str}")
