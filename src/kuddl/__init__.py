from typing import Any, Dict, Optional, cast, List, Type, Union
from itertools import chain
from functools import reduce
from importlib import import_module

import yaml

from kuddl.version import __version__

__version__ = __version__


AnyLoader = Union[yaml.BaseLoader, yaml.FullLoader, yaml.SafeLoader, yaml.Loader]
# missing yaml.UnsafeLoader # python/typeshed#5390


def _dict_union(a: Dict[Any, Any], *bs: Dict[Any, Any]) -> Dict[Any, Any]:
    if len(bs) == 0:
        return a
    return {**a, **_dict_union(*bs)}


def _eval_template(template: str, variables: Dict[str, Any]) -> str:
    return cast(str, eval(f"f{template!r}", variables))


class _Scope:
    def __init__(self, current: Dict[str, Any], parent: Optional["_Scope"] = None):
        self._current = current
        self._parent = parent

    @property
    def flattened(self) -> Dict[str, Any]:
        if self._parent is not None:
            return _dict_union(self._parent.flattened, self._current)
        return self._current


class _KuddlDict(Dict[str, Any]):
    def __kuddl_eval__(self, scope: _Scope) -> "_KuddlDict":
        scope = _Scope(current=self, parent=scope)
        for k, v in self.items():
            if hasattr(v, "__kuddl_eval__"):
                try:
                    self[k] = v.__kuddl_eval__(scope)
                except KuddlEvalException as e:
                    e.stacktrace.append(f"[{k!r}]")
                    raise
        return self


class _KuddlList(List[Any]):
    def __kuddl_eval__(self, scope: _Scope) -> "_KuddlList":
        for i, v in enumerate(self):
            if hasattr(v, "__kuddl_eval__"):
                try:
                    self[i] = v.__kuddl_eval__(scope)
                except KuddlEvalException as e:
                    e.stacktrace.append(f"[{i!r}]")
                    raise
        return self


class _KuddlEval(str):
    def __kuddl_eval__(self, scope: _Scope) -> Any:
        env = scope.flattened
        code_str = _eval_template(self, env)
        try:
            v = eval(code_str, env, {})
        except Exception as e:
            raise KuddlEvalException(repr(e)) from None
        else:
            return v


class _KuddlBlockEval(str):
    def __kuddl_eval__(self, scope: _Scope) -> Any:
        env = scope.flattened
        code_str = _eval_template(self, env)
        func_str = "\n\t".join(["def _tmp():"] + code_str.split("\n"))
        loc: Dict[str, Any] = {}
        try:
            exec(func_str, env, loc)
        except Exception as e:
            raise KuddlEvalException(repr(e)) from None
        else:
            return loc["_tmp"]()


class _KuddlImport(str):
    def __kuddl_eval__(self, scope: _Scope) -> Any:
        env = scope.flattened
        import_str = _eval_template(self, env)
        split = import_str.split(":", 1)
        if len(split) == 1:
            (module_name,) = split
            return import_module(module_name)
        elif len(split) == 2:
            module_name, object_name = split
            module = import_module(module_name)
            return reduce(getattr, object_name.split("."), module)
        raise KuddlEvalException(f"bad import specifier: {import_str}")


class _KuddlInclude(str):
    def __kuddl_eval__(self, scope: _Scope) -> Any:
        env = scope.flattened
        filename = _eval_template(self, env)
        return load(open(filename).read())


class _KuddlTemplate(str):
    def __kuddl_eval__(self, scope: _Scope) -> str:
        env = scope.flattened
        return _eval_template(self, env)


class KuddlEvalException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.stacktrace: List[str] = []

    def __str__(self) -> str:
        stacktrace = "".join(chain("root", reversed(self.stacktrace)))
        cause = super().__str__()
        return f"when evaluating {stacktrace!r}: {cause}"


def register_kuddl(loader: Type[AnyLoader]) -> Type[AnyLoader]:
    """
    Registers KUDDL constructors with the given :class:`yaml.loader`.
    """

    def _construct_sequence(loader: AnyLoader, node: yaml.SequenceNode) -> List[Any]:
        return _KuddlList(loader.construct_object(child) for child in node.value)

    def _construct_mapping(loader: AnyLoader, node: yaml.MappingNode) -> Dict[str, Any]:
        return _KuddlDict(
            (loader.construct_object(k), loader.construct_object(v))
            for k, v in node.value
        )

    def _construct_eval(loader: AnyLoader, node: yaml.ScalarNode) -> Any:
        return _KuddlEval(node.value)

    def _construct_blockeval(loader: AnyLoader, node: yaml.ScalarNode) -> Any:
        return _KuddlBlockEval(node.value)

    def _construct_importer(loader: AnyLoader, node: yaml.ScalarNode) -> Any:
        return _KuddlImport(node.value)

    def _construct_includer(loader: AnyLoader, node: yaml.ScalarNode) -> Any:
        return _KuddlInclude(node.value)

    def _construct_template(loader: AnyLoader, node: yaml.ScalarNode) -> Any:
        return _KuddlTemplate(node.value)

    loader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, _construct_sequence
    )
    loader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
    )
    loader.add_constructor("!Eval", _construct_eval)
    loader.add_constructor("!BlockEval", _construct_blockeval)
    loader.add_constructor("!Import", _construct_importer)
    loader.add_constructor("!Include", _construct_includer)
    loader.add_constructor("!Template", _construct_template)

    return loader


class KuddlLoader(yaml.FullLoader):
    """
    Default loader used by :func:`kuddl.load`.
    """


register_kuddl(KuddlLoader)


def post_process(document: Any, args: Any) -> Any:
    """
    Given a document object loaded with KUDDL extensions, evalulates the document.
    """
    if hasattr(document, "__kuddl_eval__"):
        root_scope = _Scope({"args": args, "root": document})
        return document.__kuddl_eval__(root_scope)
    return document


def load(s: str, Loader: Type[AnyLoader] = KuddlLoader, *, args: Any = None) -> Any:
    """
    Wrapper around :func:`yaml.load` which supports KUDDL extensions.

    Loads a file, evaluates KUDDL extensions, and returns the document.
    """
    document = yaml.load(s, Loader=Loader)
    return post_process(document, args)
