import yaml

from .yaml_wrappers import YamlDict, YamlList, YamlEval, YamlBlockEval, YamlImport
from ._version import __version__  # noqa


class DynamicYamlLoader(yaml.FullLoader):
    pass


def _construct_sequence(loader, node):
    return YamlList(loader.construct_object(child) for child in node.value)


def _construct_mapping(loader, node):
    make_obj = loader.construct_object
    return YamlDict((make_obj(k), make_obj(v)) for k, v in node.value)


def _construct_eval(loader, node):
    return YamlEval(node.value)


def _construct_blockeval(loader, node):
    return YamlBlockEval(node.value)


def _construct_importer(laoder, node):
    return YamlImport(node.value)


def _construct_includer(loader, node):
    return YamlInclude(node.value)


DynamicYamlLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, _construct_sequence)
DynamicYamlLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)
DynamicYamlLoader.add_constructor('!Eval', _construct_eval)
DynamicYamlLoader.add_constructor('!BlockEval', _construct_blockeval)
DynamicYamlLoader.add_constructor('!Import', _construct_importer)
DynamicYamlLoader.add_constructor('!Include', _construct_includer)


def post_process(data):
    if hasattr(data, '_dynamic_yaml_eval'):
        data._dynamic_yaml_eval(root=data, stack=[])
    return data


def load(s, Loader=DynamicYamlLoader):
    data = yaml.load(s, Loader=Loader)
    return post_process(data)
