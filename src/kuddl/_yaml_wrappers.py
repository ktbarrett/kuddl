class YamlDict(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        return super().__getattribute__(key)

    def _kuddl_eval(self, scope):
        scope = scope._add(self)
        for k, v in self.items():
            if hasattr(v, "_kuddl_eval"):
                try:
                    self[k] = v._kuddl_eval(scope)
                except YamlEvalException as e:
                    e.stacktrace.append(f".{k}")
                    raise
        return self


class YamlList(list):
    def _kuddl_eval(self, scope):
        for i, v in enumerate(self):
            if hasattr(v, "_kuddl_eval"):
                try:
                    self[i] = v._kuddl_eval(scope)
                except YamlEvalException as e:
                    e.stacktrace.append(f"[{i}]")
                    raise
        return self


class YamlEvalException(Exception):
    def __init__(self):
        super().__init__()
        self.stacktrace = []

    def __str__(self):
        stacktrace = "".join(reversed(self.stacktrace))
        return f"when evaluating 'root{stacktrace}'"


class YamlEval(str):
    def _kuddl_eval(self, scope):
        env = scope._freeze()
        code_str = self.format(**env)
        try:
            v = eval(code_str, env, {})
        except Exception:
            raise YamlEvalException()
        else:
            return v


class YamlBlockEval(str):
    def _kuddl_eval(self, scope):
        env = scope._freeze()
        code_str = self.format(**env)
        func_str = "\n\t".join(["def _tmp():"] + code_str.split("\n"))
        loc = {}
        try:
            exec(func_str, env, loc)
        except Exception:
            raise YamlEvalException()
        else:
            return loc["_tmp"]()


class YamlImport(str):
    def _kuddl_eval(self, scope):
        env = scope._freeze()
        import_str = self.format(**env)
        spl = import_str.split(":")
        if len(spl) == 1:
            (name,) = spl
            return __import__(name, globals(), {})
        elif len(spl) == 2:
            name, item = spl
            return getattr(__import__(name, globals(), {}), item)
        else:
            raise YamlEvalException(f"bad import specifier: {import_str}")


class YamlInclude(str):
    def _kuddl_eval(self, scope):
        env = scope._freeze()
        filename = self.format(**env)
        from . import load

        return load(open(filename).read())


class YamlTemplate(str):
    def _kuddl_eval(self, scope):
        env = scope._freeze()
        return self.format(**env)
