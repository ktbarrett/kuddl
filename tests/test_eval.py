from dynamic_yaml import load


def test_eval_1():
    s = """
    !Eval 2+2
    """
    document = load(s)
    assert document == 4


def test_eval_2():
    s = """
    a: 5
    b: !Eval a * 3
    """
    document = load(s)
    assert document.b == 15
