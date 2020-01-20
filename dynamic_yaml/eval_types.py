
class YamlEval(str):

    def format(self, *args, **kwargs):
        return eval(super().format(*args, **kwargs), globals(), {})


def indent_lines(s):
    return '\n\t'.join(s.split('\n'))


class YamlBlockEval(str):

    def format(self, *args, **kwargs):
        code_str = super().format(*args, **kwargs)
        func_str = '\n\t'.join(["def _tmp():"] + code_str.split('\n'))
        loc = {}
        exec(func_str, globals(), loc)
        return loc["_tmp"]()

