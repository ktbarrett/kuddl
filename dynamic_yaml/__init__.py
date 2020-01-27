import yaml

from ._version import __version__  # noqa


def register_dynamic_yaml(Loader):
    from ._yaml_wrappers import YamlDict, YamlList, YamlEval, YamlBlockEval, YamlImport, YamlInclude

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

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, _construct_sequence)
    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)
    Loader.add_constructor('!Eval', _construct_eval)
    Loader.add_constructor('!BlockEval', _construct_blockeval)
    Loader.add_constructor('!Import', _construct_importer)
    Loader.add_constructor('!Include', _construct_includer)


class DynamicYamlLoader(yaml.FullLoader):
    pass


register_dynamic_yaml(DynamicYamlLoader)


def post_process(document, args):
    from ._scope import NullScope
    if hasattr(document, '_dynamic_yaml_eval'):
        document._dynamic_yaml_eval(NullScope(args=args, root=document))
    return document


def load(s, args={}, Loader=DynamicYamlLoader):
    document = yaml.load(s, Loader=Loader)
    return post_process(document, args)
