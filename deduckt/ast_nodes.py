import sys
import ast
import json
from type_system import *

LABEL = 'Variable'


def merge(a, b):
    c = a.copy()
    c.update(b)
    return c


BIGGEST_INT = 9223372036854775807
SMALLEST_INT = -9223372036854775808

KINDS = {'Number': 'Int'}
method_nodes = {}

PROJECT_DIR = ''
PACKAGE = ''

def load_namespace(filename):
    '''
    generates namespace currently based on directories
    # TODO check __init__.py
    '''
    if not filename.startswith(PROJECT_DIR) or filename[-3:] != '.py':
        return ''
    else:
        tokens = filename[len(PROJECT_DIR):].split('/')
        return PACKAGE + '.'.join(tokens)[:-3]


class JsonTranslator:

    def __init__(self):
        self.source = []
        self.line = 0
        self.column = 0
        self.nodes_by_line = {}
        self.current_class = ''
        self.current_def = ''

    def translate(self, child):
        return (getattr(self, 'translate_%s' % type(child).__name__.lower(), None) or
                self.translate_child)(child)

    def translate_file(self, root_node, source, filename):
        self.source = source.split('\n')
        self.filename = filename
        result = self.translate(root_node)
        result["nodes_by_line"] = self.nodes_by_line

        return result

    def get_kind(self, t):
        return KINDS.get(t, t)

    def translate_classdef(self, child):
        value = {'kind': 'Class', 'label': child.name, 'fields': [], 'methods': []}
        self.current_class = child.name
        methods = [self.translate(method) for method in child.body if isinstance(method, ast.FunctionDef)]
        self.current_class = ''
        value['methods'] = [{'label': method['label'], 'node': method} for method in methods]
        return value

    def translate_functiondef(self, node):
        method = {'kind': 'NodeMethod', 'label': node.name, 'args': []}
        children = [{'kind': 'variable', 'label': child.arg} for child in node.args.args]
        method['args'] = children
        code = [self.translate(child) for child in node.body]
        method['code'] = code
        namespace = load_namespace(self.filename)
        name = '%s%s%s#%s' % (namespace, '.' if self.current_class else '', self.current_class, node.name)
        method['return_type'] = PY_NONE.as_json()
        method_nodes[name] = method
        return method
        

    def translate_module(self, child):
        value = {'classes': [], 'main': []}
        for line in child.body:
            if isinstance(line, ast.ClassDef):
                value['classes'].append(self.translate(line))
            else:
                value['main'].append(self.translate(line))
        return value

    def translate_call(self, child):
        line = getattr(child, 'lineno', -1)
        column = getattr(child, 'col_offset', -1)
        call = {'kind': 'Call', 'children': [], 'line': line, 'column': column, 'typ': PY_NONE.as_json()}
        call['children'].append(self.translate(child.func))
        call['children'].extend([self.translate(arg) for arg in child.args])
        nodes = self.nodes_by_line.setdefault(line, [])
        nodes.append(call)
        return call

    def translate_expr(self, child):
        return self.translate(child.value)

    def translate_child(self, child):
        line = getattr(child, 'lineno', -1)
        column = getattr(child, 'col_offset', -1)
        if isinstance(child, ast.AST):
            node_type = type(child).__name__
            left = {
                'kind': '%s' % self.get_kind(node_type),
                'children': [
                    self.translate(getattr(child, label))
                    for label in child._fields
                    if label not in {'ctx'}
                ],
                'line': line,
                'column': column
            }

            while len(left['children']) == 1 and left['children'][0]['kind'] == 'Code':
                left['children'] = left['children'][0]['children']

            if node_type == "Call":
                nodes = self.nodes_by_line.setdefault(line, [])
                nodes.append(left)

            return left
        elif isinstance(child, list):
            return {
                'kind': 'Code',
                'children': [self.translate(son) for son in child],
                'line': line,
                'column': column
            }
        elif child is None:
            return {
                'kind': 'Nil',
                'line': line,
                'column': column
            }
        elif isinstance(child, bytes):
            return {
                'kind': 'Bytes',
                's': str(child),
                'line': line,
                'column': column
            }
        elif isinstance(child, int):
            if child < SMALLEST_INT or child > BIGGEST_INT:
                return {
                    'kind': 'PyHugeInt',
                    'h': str(child),
                    'line': line,
                    'column': column
                }
            else:
                return {
                    'kind': 'Int',
                    'i': child,
                    'line': line,
                    'column': column
                }
        elif isinstance(child, float):
            return {
                'kind': 'Float',
                'f': child,
                'line': line,
                'column': column
            }
        else:
            return {
                'kind': 'String',
                'text': str(child),
                'line': line,
                'column': column
            }

    def translate_nameconstant(self, child):
        line = getattr(child, 'lineno', -1)
        column = getattr(child, 'col_offset', -1)
        return {
            'kind': LABEL,
            'label': str(child.value),
            'line': line,
            'column': column
        }

    def translate_name(self, child):
        line = getattr(child, 'lineno', -1)
        column = getattr(child, 'col_offset', -1)
        return {
            'kind': LABEL,
            'label': child.id,
            'line': line,
            'column': column
        }

    def translate_num(self, child):
        line = getattr(child, 'lineno', -1)
        column = getattr(child, 'col_offset', -1)
        if isinstance(child, ast.Num):
            if isinstance(child.n, int):
                if child.n < SMALLEST_INT or child.n > BIGGEST_INT:
                    return {
                        'kind': 'PyHugeInt',
                        'h': str(child.n),
                        'line': line,
                        'column': column
                    }
                else:
                    return {
                        'kind': 'Int',
                        'i': child.n,
                        'line': line,
                        'column': column
                    }
            else:
                return {
                    'kind': 'Float',
                    'f': child.n,
                    'line': line,
                    'column': column
                }
        else:
            if isinstance(child, int):
                if child < SMALLEST_INT or child > BIGGEST_INT:
                    return {
                        'kind': 'PyHugeInt',
                        'h': str(child),
                        'line': line,
                        'column': column
                    }
                else:
                    return {
                        'kind': 'Int',
                        'i': child,
                        'line': line,
                        'column': column
                    }
            else:
                return {
                    'kind': 'Float',
                    'f': child,
                    'line': line,
                    'column': column
                }

    def translate_str(self, child):
        line = getattr(child, 'lineno', -1)
        column = getattr(child, 'col_offset', -1)
        if isinstance(child, ast.Str):
            return {
                'kind': 'String',
                's': child.s,
                'line': line,
                'column': column
            }
        else:
            return {
                'kind': 'String',
                's': child,
                'line': line,
                'column': column
            }

    def translate_bytes(self, child):
        line = getattr(child, 'lineno', -1)
        column = getattr(child, 'col_offset', -1)
        if isinstance(child, ast.Bytes):
            return {
                'kind': 'PyBytes',
                's': str(child.s)[2:-1],
                'line': line,
                'column': column
            }
        else:
            return {
                'kind': 'PyBytes',
                's': str(child)[2:-1],
                'line': line,
                'column': column
            }


def nodes_from_source(source, filename):
    return JsonTranslator().translate_file(ast.parse(source), source, filename)


def nodes_from_file(filename):
    with open(filename, 'r') as f:
        return nodes_from_source(f.read(), filename)


if __name__ == '__main__':
    if '.py' not in sys.argv[1]:
        source_path = '%s.py' % sys.argv[1]
    else:
        source_path = sys.argv[1]

    nodes = nodes_from_file(source_path)
    print(json.dumps(nodes, indent=4))
