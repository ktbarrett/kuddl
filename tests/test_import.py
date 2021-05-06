from kuddl import load
import textwrap


def test_import_1():
    s = textwrap.dedent("""
    ceil: !Import math:ceil
    log2: !Import math:log2
    value: !Eval ceil(log2(8))
    value2: !Eval ceil(log2(9))
    """)
    document = load(s)
    assert document.value == 3
    assert document.value2 == 4
