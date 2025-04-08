from collections import namedtuple

LexToken = namedtuple('LexToken', ['type', 'value', 'lineno', 'lexpos'])

tokens = (
    LexToken('SET','set',1,0),
    LexToken('IDENTIFIER','x',1,4),
    LexToken('EQUAL','=',1,6),
    LexToken('NUMBER',10,1,8)
)

class Parser :
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1

    def match(self, expected_type):
        tok = self.current()
        if tok and tok.type == expected_type:
            self.advance()
            return tok
        else:
            raise SyntaxError(f"Expected {expected_type} but got {tok}")
        
    def parse_var_assign(self):
        self.match('SET')
        
        identifier_token = self.match('IDENTIFIER')
        self.match('EQUAL')  # Match '='

        number_token = self.match('NUMBER')
        value_node = NumberNode(number_token.value)
        
        return VarAssignNode(identifier_token.value, value_node)
        
        
class VarAssignNode:
    def __init__(self, name, value):
        self.name = name      # e.g. 'x'
        self.value = value    # an AST node (like NumberNode)

class NumberNode:
    def __init__(self, value):
        self.value = value    # e.g. 5

parser = Parser(tokens)
ast = parser.parse_var_assign()

print(f"VarAssignNode(name={ast.name}, value={ast.value.value})")

class Interpreter:
    def __init__(self):
        self.variables = {}

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_VarAssignNode(self, node):
        value = self.visit(node.value)  # Recursively visit right side
        self.variables[node.name] = value
        return value

    def visit_NumberNode(self, node):
        return node.value

parser = Parser(tokens)
ast = parser.parse_var_assign()

interpreter = Interpreter()
result = interpreter.visit(ast)

print(interpreter.variables)  # {'x': 5}
