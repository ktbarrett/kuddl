from kuddl import load, KuddlEvalException
import textwrap
import pathlib
import re


def test_eval():
    s = textwrap.dedent(
        """
        !Eval 2+2
        """
    )
    document = load(s)
    assert document == 4


def test_lexical_capture():
    s = textwrap.dedent(
        """
        a: 5
        b: !Eval a * 3
        """
    )
    document = load(s)
    assert document["b"] == 15


def test_accesing_children_in_lexical_capture():
    s = textwrap.dedent(
        """
        a:
          - b: 6
          - 89
        c: !Eval a[0]['b'] / 3
        """
    )
    document = load(s)
    assert document["c"] == 2


def test_global():
    s = textwrap.dedent(
        """
        a:
            b: 6
        c: !Eval root["a"]['b'] / 3
        """
    )
    document = load(s)
    assert document["c"] == 2


def test_args():
    s = textwrap.dedent(
        """
        a: !Eval args['a'] + 6
        """
    )
    document = load(s, args={"a": 4})
    assert document["a"] == 10


def test_eval_block():
    s = textwrap.dedent(
        """
        !BlockEval |
            a = []
            for i in range(10):
                a.append(i*i)
            return a
        """
    )
    document = load(s)
    assert len(document) == 10
    assert document[3] == 9


def test_template():
    s = textwrap.dedent(
        """
        a:
            b: 5
        c: !Template 1{a['b']}
        """
    )
    document = load(s)
    assert document["c"] == "15"


def test_import():
    s = textwrap.dedent(
        """
        math: !Import math
        from_iterable: !Import itertools:chain.from_iterable
        value: !Eval math.ceil(math.log2(8))
        bad_example: !Eval list(from_iterable((range(i) for i in range(4))))
        """
    )
    document = load(s)
    assert document["value"] == 3
    assert document["bad_example"] == [0, 0, 1, 0, 1, 2]


def test_include():
    currdir = pathlib.Path(__file__).parent
    s = textwrap.dedent(
        """
        extra: !Include "{args['currdir']}/extra.yaml"
        a: !Eval "extra['a']"
        """
    )
    document = load(s, args={"currdir": currdir})
    assert document["extra"]["a"] == 5
    assert document["a"] == 5


def test_stacktrace():
    s = textwrap.dedent(
        """
        a:
            b:
              - c: !Eval "object() * 8"
        """
    )
    try:
        load(s)
    except KuddlEvalException as e:
        assert re.search(r"root\[.a.\]\[.b.\]\[0\]\[.c.\]", str(e))
        assert "TypeError" in str(e)
    else:
        assert False, "should have thrown"
