from dynamic_yaml import load
import textwrap


def test_eval_block():
    s = textwrap.dedent("""
    !BlockEval |
        a = []
        for i in range(10):
            a.append(i*i)
        return a
    """)
    document = load(s)
    assert len(document) == 10
    assert document[3] == 9
