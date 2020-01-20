import yaml

from .yaml_wrappers import YamlDict, YamlList
from ._version import __version__


def load(s):

    def _construct_sequence(loader, node):
        return YamlList(loader.construct_object(child) for child in node.value)

    def _construct_mapping(loader, node):
        make_obj = loader.construct_object
        return YamlDict((make_obj(k), make_obj(v)) for k, v in node.value)

    yaml.FullLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, _construct_sequence)
    yaml.FullLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)

    data = yaml.load(s, Loader=yaml.FullLoader)

    if hasattr(data, '_dynamic_yaml_eval'):
        data._dynamic_yaml_eval(root=[], scope=[])
    return data
