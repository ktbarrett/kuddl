from dynamic_yaml import load


def test_include_1(datadir):
    s = f"""
    other_file: !Include {datadir}/example.yaml
    """
    document = load(s)
    assert document.other_file.e == "a3"
