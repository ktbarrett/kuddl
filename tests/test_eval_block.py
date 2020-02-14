from dynamic_yaml import load


def test_eval_block():
    s = """
    !BlockEval |
        a = []
        for i in range(10):
            a.append(i*i)
        return a
    """
    document = load(s)
    assert len(document) == 10
    assert document[3] == 9
