import yaml

from ._version import __version__  # noqa


def register_kuddl(Loader):
    from ._yaml_wrappers import YamlDict, YamlList, YamlEval, YamlBlockEval, YamlImport, YamlInclude, YamlTemplate

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

    def _construct_template(loader, node):
        return YamlTemplate(node.value)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, _construct_sequence)
    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)
    Loader.add_constructor('!Eval', _construct_eval)
    Loader.add_constructor('!BlockEval', _construct_blockeval)
    Loader.add_constructor('!Import', _construct_importer)
    Loader.add_constructor('!Include', _construct_includer)
    Loader.add_constructor('!Template', _construct_template)


class KuddlLoader(yaml.FullLoader):
    pass


register_kuddl(KuddlLoader)


def post_process(document, args):
    from ._scope import NullScope
    if hasattr(document, '_kuddl_eval'):
        return document._kuddl_eval(NullScope(args=args, root=document))
    return document


def load(s, args={}, Loader=KuddlLoader):
    document = yaml.load(s, Loader=Loader)
    return post_process(document, args)
