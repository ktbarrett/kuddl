
class YamlStructure():

    def _dynamic_yaml_eval(self, scope):
        scope = scope._add(self)
        for k, v in self.items():
            if hasattr(v, '_dynamic_yaml_eval'):
                try:
                    self[k] = v._dynamic_yaml_eval(scope)
                except YamlEvalException as e:
                    e.stacktrace.append(f"{k}")
                    raise
            elif isinstance(v, str):
                self[k] = v.format(**scope._freeze())
        return self


class YamlDict(YamlStructure, dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return super().__getattribute__(key)


class YamlList(YamlStructure, list):

    pass


class YamlEvalException(Exception):

    def __init__(self):
        super().__init__()
        self.stacktrace = []

    def __str__(self):
        stacktrace = '.'.join(reversed(self.stacktrace))
        return f"when evaluating '{stacktrace}'"


class YamlEval(str):

    def _dynamic_yaml_eval(self, scope):
        env = scope._freeze()
        code_str = self.format(**env)
        try:
            v = eval(code_str, env, {})
        except Exception:
            raise YamlEvalException()
        else:
            return v


class YamlBlockEval(str):

    def _dynamic_yaml_eval(self, scope):
        env = scope._freeze()
        code_str = self.format(**env)
        func_str = '\n\t'.join(["def _tmp():"] + code_str.split('\n'))
        loc = {}
        try:
            exec(func_str, env, loc)
        except Exception:
            raise YamlEvalException()
        else:
            return loc["_tmp"]()


class YamlImport(str):

    def _dynamic_yaml_eval(self, scope):
        env = scope._freeze()
        import_str = self.format(**env)
        spl = import_str.split(":")
        if len(spl) == 1:
            name, = spl
            return __import__(name, globals(), {})
        elif len(spl) == 2:
            name, item = spl
            return getattr(__import__(name, globals(), {}), item)
        else:
            raise YamlEvalException(f"bad import specifier: {import_str}")


class YamlInclude(str):

    def _dynamic_yaml_eval(self, scope):
        env = scope._freeze()
        filename = self.format(**env)
        from . import load
        return load(open(filename).read())
