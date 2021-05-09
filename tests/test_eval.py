from kuddl import load
import textwrap


def test_eval_1():
    s = textwrap.dedent(
        """
        !Eval 2+2
        """
    )
    document = load(s)
    assert document == 4


def test_eval_2():
    s = textwrap.dedent(
        """
        a: 5
        b: !Eval a * 3
        """
    )
    document = load(s)
    assert document.b == 15
