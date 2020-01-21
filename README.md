dynamic-yaml
============

Dynamic YAML is a couple of classes and functions that add extra functionality to YAML that turns it into a great configuration language for Python.

YAML already provides:

* A very readable and clean syntax
* Infinitely nestable key:value pairs
* Sequence types
* A regulated portable syntax that conforms to strict standards

In addition, the PyYAML parser provides:

* Automatic type identification (a result of implementing the YAML standard)

Finally, the classes introduced by Dynamic YAML enable:

* Dynamic string resolution
* Evaluation of arbitrary Python code

Dynamic PyYAML requires PyYAML (https://bitbucket.org/xi/pyyaml).

Usage
-----
The key feature that was introduced is the ability for a string scalar to reference other parts of the configuration tree. This is done using the Python string formatting syntax. The characters '{' and '}' enclose a reference to another entry in the configuration structure. The reference takes the form key1.key2 where key1 maps to another mapping object and can be found in the root mapping, and key2 can be found in key1's mapping object. Multiple levels of nesting can be used (eg. key1.key2.key3 etc...).

An example yaml configuration:
```yaml
project_name: hello-world
randint : !Import "random:randint"
dirs:
    home: /home/user
    venv: "{dirs.home}/venvs/{project_name}"
    data: "{venv}/data"
    databases:
        - "{dirs.data}/db0"
        - "{dirs.data}/db1"
        - "{data}/db_test"
exes:
    main: "{dirs.home}/main"
test:
  wow : 2
wew: !Eval "test.wow+2"
wewblock: !BlockEval |
    a = []
    for i in range({wew}):
        a.append(randint(0, i)*2)
    return a
a :
  arg : 2
  value : &func !Eval "arg * 2"
b :
  arg : 3
  value : *func
```

Reading in a yaml file:

```python
import dynamic_yaml

with open('/path/to/file.yaml') as fileobj:
    cfg = dynamic_yaml.load(fileobj)
```

Now, the entry `cfg.dirs.venv` will resolve to `"/home/user/venvs/hello-world"`.

Installation
------------

First clone the repo,

```bash
git clone https://github.com/ktbarrett/dynamic-yaml.git
```

Then you can install it,

```bash
pip install dynamic-yaml
```

Restrictions
------------

Due to the short amount of time I was willing to spend on working upon this, there are a few restrictions required for a valid YAML configuration file.

* **Wild card strings must be surrounded by quotes.** Braces ('{' and '}') in a YAML file usually enclose a mapping object. However, braces are also used by the Python string formatting syntax to enclose a reference. As there is no way to change either of these easily, strings that contain wildcards must be explicitly declared using single or double quotes to enclose them.
* **Variables are always dynamically resolved.** This possibly introduces significant slow downs, but hopefully your configuration object isn't too big anyway.


Differences
-----------

This is a fork of [childsish's project](https://github.com/childsish/dynamic-yaml) if you missed it.
I was looking to write a tool to do something similar and liked his implementation so I used it as a starting point.
However, I wanted a few extra features and disliked some of the original implementation.

 - Removed `__setitem__` behavior that attempts to enforce all YAML structure as the custom objects.
   - There are *numerous* issues with the implementation.
   - I did not need the need to dump the object in unresolved format.
 - Removed `__repr__` behavior which I assume was there to aid in dumping the object in unresolved format.
 - Cached resolved values for performance
 - Added more variables
   - Variable reference is now lexically scoped, not always from the root
   - Variable reference from root scope via special variable `root`
   - Variable reference of current object via special variable `this`. Useful for lists and referencing deeper into table heirarchies.
 - Fixed some bugs with `YamlList`
 - Refactor
 - Added `Eval` and `EvalBlock` tags to support arbitrary Python code execution in objects
