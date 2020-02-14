from dynamic_yaml import load


def test_template_1():
    s = """
    a:
        b: 5
    c: !Template 1{a.b}
    d:
        e: !Template lol {c}
    """
    document = load(s)
    assert document.c == "15"
    assert document["d"].e == "lol 15"
