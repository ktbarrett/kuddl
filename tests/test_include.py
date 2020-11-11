from dynamic_yaml import load
import textwrap


def test_include_1(datadir):
    s = textwrap.dedent(f"""
    other_file: !Include {datadir}/example.yaml
    """)
    document = load(s)
    assert document.other_file.e == "a3"
