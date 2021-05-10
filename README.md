[![regressions](https://github.com/ktbarrett/kuddl/actions/workflows/tests.yml/badge.svg)](https://github.com/ktbarrett/kuddl/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/ktbarrett/kuddl/branch/master/graph/badge.svg?token=N7CS5QJ9DB)](https://codecov.io/gh/ktbarrett/kuddl)

# Kaleb's (otherwise) Untitled Data Description Language - KUDDL

Combines the cleanliness of YAML, the power of Python, and some ingenuity.

> It's like a hug — Paul U.

## How It Works

KUDDL uses YAML constructors to turn purely declarative values into dynamic values.

This is accomplished by evaluating Python expressions in strings.
The `!Eval` constructor evaluates a single Python expression using Python's `eval`.
`BlockEval` offers support for multiple statements; the value `return`ed becomes the value of the document node.

```yaml
four: !Eval "2 * 2"
fibs: !BlockEval |
  c = [1, 1]
  for i in range(5):
    c.append(c[-1] + c[-2])
  return c
```

```python
doc = kuddl.load(example_str)
assert doc["four"] == 4
assert doc["fibs"] == [1, 1, 2, 3, 5, 8, 13]
```

KUDDL allows you to reference other values in the hierarchy in a lexical way.
There is also the special variable 'global' which allows you to override lexical scoping;
and 'args' which allows the user to pass arguments to the YAML "script".

```yaml
a: 2
b:
    value: !Eval "a * 3"
c:
- more: !Eval "str(b['value'])"
- !Eval "global['c'][0]['more'] * 3"
```

```python
doc = kuddl.load(example_str)
assert doc["b"] == 6
assert doc["c"][0]["more"] == "6"
assert doc["c"][1] == "666"
```

You can describe string templates in KUDDL using the `!Template` constructor.
Variables are reference in the same way as in the rest of KUDDL.
Python formatting options that are supported by f-strings are supported in `!Template`s as well.

```yaml
a:
  b: 5
c: !Template 1{a['b']}
```

```python
doc = kuddl.load(example_str)
assert doc["c"] == "15"
```

It's worth noting that all other KUDDL constructors are also templates.
This allows you to do some basic string-based metaprogramming in KUDDL.

Import Python classes, functions, values, etc. using `!Import`.
Import strings follow the convention: `package.module:object.value`.
Combine this with variables for more powerful expressions.

```yaml
ceil: !Import math:ceil
log2: !Import math:log2
value: !Eval ceil(log2(8))
value2: !Eval ceil(log2(9))
```

```python
doc = kuddl.load(example_str)
assert doc["value"] == 3
assert doc["value2"] == 4
```

Split your YAMLs into multiple files and use `!Include` to join the documents together.
Include paths can be relative (to the main process), or absolute.

```yaml
other_doc: !Include "./other.yaml"
myvar: !Eval other_doc.special_var
```
