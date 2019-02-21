class PyType:

    def __str__(self):
        return repr(self)


class PySimple(PyType):

    def __init__(self, label):
        self.label = label

    def __repr__(self):
        return '<%s>' % self.label

    def __eq__(self, other):
        return isinstance(other, PySimple) and other.label == self.label

    def __hash__(self):
        return hash(self.label)

    def as_json(self):
        return {
            'kind': 'Simple',
            'label': self.label
        }


# Method: interlang, but here type is PyFunction, mapped to 'Method'
class PyFunction(PyType):

    def __init__(self, label, args, variables, return_type):
        self.label = label
        self.args = args
        self.variables = variables
        self.return_type = return_type

    def __repr__(self):
        return self.label + '()'

    def __eq__(self, other):
        # print(other.args[0].name, other.args[0].type)
        # print(self.args[0].name, self.args[0].type)
        # print(other.args[0] == self.args[0])
        # print()
        return isinstance(other, PyFunction) and \
            other.label == self.label and \
            other.args == self.args

    def as_json(self):
        return {
            'kind': 'Method',
            'label': self.label,
            'args': [t.type.as_json() for t in self.args],
            'variables': [{'label': t.label, 'type': t.type.as_json()} for t in self.variables],
            'returnType': self.return_type.as_json()
        }

    def __hash__(self, other):
        return hash(self.label) ^ \
            hash(tuple(t.label for t in self.args)) ^ \
            hash(tuple(t.type for t in self.args))


class PyFunctionOverloads(PyType):

    def __init__(self, label, overloads):
        self.label = label
        self.overloads = overloads

    def __repr__(self):
        return self.label + '()'

    def __eq__(self, other):
        return isinstance(other, PyFunctionOverloads) and \
            other.label == self.label and \
            other.overloads == self.overloads

    def as_json(self):
        return {
            'kind': 'MethodOverload',
            'label': self.label,
            'overloads': [t.as_json() for t in self.overloads]
        }


class PyGeneric(PyType):

    def __init__(self, klass, length):
        self.klass = klass
        self.length = length

    def gen(self, types):
        return PyConcrete(self, types)

    def __eq__(self, other):
        return isinstance(other, PyGeneric) and \
            other.klass == self.klass and \
            other.length == self.length

    def __repr__(self):
        return '<generic %s>' % self.klass

    def __hash__(self):
        return hash(self.klass) ^ hash(self.length)

    def as_json(self):
        return {
            'kind': 'Generic',
            'klass': self.klass,
            'length': self.length
        }


class PyConcrete(PyType):

    def __init__(self, base, types):
        self.base = base
        self.types = types

    def __eq__(self, other):
        return isinstance(other, PyConcrete) and \
            other.base == self.base and \
            other.types == self.types

    def __repr__(self):
        return '<%s[%s]>' % (
            self.base.klass,
            ' '.join([repr(type) for type in self.types])
        )

    def __hash__(self):
        return hash(self.base) ^ hash(tuple(self.types))

    def as_json(self):
        return {
            'kind': 'Concrete',
            'label': self.base.klass,
            'types': [t.as_json() for t in self.types]
        }


class PyOptional(PyType):

    def __init__(self, type):
        self.type = type

    def __hash__(self):
        return hash(self.type)

    def __eq__(self, other):
        return isinstance(other, PyOptional) and other.type == self.type

    def __repr__(self):
        return repr(self.type) + '?'

    def as_json(self):
        return {
            'kind': 'Optional',
            'type': self.type.as_json()
        }


class PyUnion(PyType):

    def __init__(self, *types):
        self.types = types

    def __hash__(self):
        return hash(tuple(self.types))

    def __eq__(self, other):
        return isinstance(other, PyUnion) and other.types == self.types

    def __repr__(self):
        return ' #|# '.join(map(repr, self.types))

    def as_json(self):
        return {
            'kind': 'PyTypeUnion',
            'types': [t.as_json() for t in self.types]
        }


class PyObject(PyType):

    def __init__(self, label, base, fields):
        self.label = label
        self.base = None  # no multiple
        self.inherited = False
        self.fields = fields

    def __hash__(self):
        return hash(self.label) ^ hash(tuple(self.fields))

    def __eq__(self, other):
        return isinstance(other, PyObject) and other.label == self.label

    def __repr__(self):
        return self.label

    def as_json(self):
        return {
            'kind': 'Object',
            'label': self.label,
            'base': None if self.base is None else self.base.as_json(),
            'inherited': self.inherited,
            'fields': [
                {'label': label, 'type': field.as_json()}
                for label, field
                in self.fields.items()
            ]
        }


class PyTuple(PyType):

    def __init__(self, elements):
        self.elements = elements

    def __hash__(self):
        return hash(tuple(self.elements))

    def __eq__(self, other):
        return isinstance(other, PyTuple) and self.elements == other.elements

    def __repr__(self):
        return '()'

    def as_json(self):
        return {
            'kind': 'Tuple',
            'elements': [element.as_json() for element in self.elements]
        }


class PyNone(PyType):

    def __repr__(self):
        return '<None>'

    def as_json(self):
        return {
            'kind': 'Simple',
            'label': 'Void'
        }


PY_INT = PySimple('Int')
PY_FLOAT = PySimple('Float')
PY_STR = PySimple('String')
PY_BOOL = PySimple('Bool')
PY_NONE = PyNone()
PY_LIST = PyGeneric('List', 1)
PY_DICT = PyGeneric('Hash', 2)
PY_TUPLE = PyTuple

NoneType = type(None)

KNOWN = {
    float:       PY_FLOAT,
    int:         PY_INT,
    str:         PY_STR,
    bool:        PY_BOOL,
    NoneType:    PY_NONE,
    list:        PY_LIST,
    dict:        PY_DICT,
    tuple:       PY_TUPLE
}


class Variable:

    def __init__(self, name, type):
        self.label = name
        self.type = type

    def __eq__(self, other):
        return other.label == self.label and other.type == self.type


def pyunify(*types):
    flat = set(flatify(types))
    normal = []
    result = {}
    for element in flat:
        if isinstance(element, PyConcrete) and element.base.length == 1:
            if element.base not in result:
                result[element.base] = []
            result[element.base].append(element)
        else:
            normal.append(element)

    for base, elements in result.items():
        type = pyunify(*[element.types[0] for element in elements])
        normal.append(type)

    if len(normal) == 1:
        return normal[0]
    elif PY_NONE in normal:
        index = normal.index(PY_NONE)
        real = normal[:index] + normal[index + 1:]
        if len(real) == 1:
            return PyOptional(real[0])
        else:
            return PyOptional(PyUnion(*real))
    else:
        return PyUnion(*normal)


def flatify(types):
    result = []
    for type in types:
        if isinstance(type, PyOptional):
            result += flatify([type.type, PY_NONE])
        elif not isinstance(type, PyUnion):
            result.append(type)
        else:
            result += flatify(type.types)
    return result
