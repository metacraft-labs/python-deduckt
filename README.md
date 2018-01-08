# python-deduckt

Deduct the types used in a Python program based on recording runtime types. 
Created for the goals of [py2nim](https://github.com/metacraft-labs/py2nim)


## How to use

python-deduckt (also launched with `python-deduckt/deduckt/main.py`) is a drop-in replacement for
the python interpreter. 

Each traced python execution will update the `python-deduckt.json` file
stored in the current directory, which describes the obtained static call graph and the inferred
types of each function definition.

```bash
python-deduckt test.py args
```

## Results

The format is

```python
{
    "<pythonName>": {
        <typeAnnotation>
    }
}
```

Python name

```python
"<namespaces>.<name>"
```

name

```python
"<name>" # const
"<name>" # class
"#<name>" # function
"<class>#<name>" # method
```

Variables 

```python
{
    "name": <name>,
    "type": <typeAnnotation>
}
```

A type annotation can be a class, function description or an atomic type.


```python
{
    "kind": "PyTypeFunction",
    "label": <name>,
    "args": [<variable>],
    "variables": [<variable>],
    "returnType": <typeAnnotation>
}
```

```python
{
    "kind": "PyTypeObject",
    "label": <name>,
    "fields": [<variable>]
}
```

Full doc: todo

## FAQ

* Can I generate mypy annotations with it?

It's fully possible to generate very useful mypy annotations from the data that you record.
However that hasn't been our usecase, but contributions are welcome

* Why does it analyze all the events?

In the future we might add an option to trace only a statistically significant part of them.
It's not a huge priority for our usecase, as we used it for [py2nim](https://github.com/metacraft-labs/py2nim).
A porting task is not something that would be ran often and better type information is more important than speed.

* Why deduckt

python-deduckt: deduct duck typing

## LICENSE

The MIT License (MIT)

Copyright (c) 2017-2018 Zahary Karadjov, Alexander Ivanov
