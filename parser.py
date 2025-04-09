# PARSER

from collections import namedtuple

LexToken = namedtuple('LexToken', ['type', 'value', 'lineno', 'lexpos'])

tokens = (
    LexToken('SET', 'set', 1, 0),
    LexToken('IDENTIFIER', 'x', 1, 4),
    LexToken('EQUAL', '=', 1, 6),
    LexToken('NUMBER', 10, 1, 8),

    LexToken('SET', 'set', 1, 0),
    LexToken('IDENTIFIER', 'y', 1, 4),
    LexToken('EQUAL', '=', 1, 6),
    LexToken('NUMBER', 15, 1, 8),
    
    LexToken('OUTPUT', 'output', 2, 0),
    LexToken('IDENTIFIER', 'x', 2, 7),
    
    LexToken('OUTPUT', 'output', 2, 0),
    LexToken('IDENTIFIER', 'y', 2, 7),
)

class Parser:
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

    def parse_statements(self):
        statements = []

        while self.current() is not None:
            tok_type = self.current().type

            if tok_type == 'SET':
                statements.append(self.parse_var_assign())
            elif tok_type == 'OUTPUT':
                statements.append(self.parse_output())
            else:
                raise SyntaxError(f"Unexpected token type: {tok_type}")

        return statements

    def parse_var_assign(self):
        self.match('SET')
        identifier_token = self.match('IDENTIFIER')
        self.match('EQUAL')  # Match '='
        number_token = self.match('NUMBER')

        value_node = NumberNode(number_token.value)
        return VarAssignNode(identifier_token.value, value_node)

    def parse_output(self):
        self.match('OUTPUT')
        tok = self.current()

        if tok.type == 'STRING':
            self.advance()
            return OutputNode(StringNode(tok.value))

        elif tok.type == 'IDENTIFIER':
            self.advance()
            return OutputNode(VarAccessNode(tok.value))

        else:
            raise SyntaxError(f"Expected STRING or IDENTIFIER after 'output', got {tok}")

        
        
class VarAssignNode:
    def __init__(self, name, value):
        self.name = name      # e.g. 'x'
        self.value = value    # an AST node (like NumberNode)

class NumberNode:
    def __init__(self, value):
        self.value = value    # e.g. 5

class StringNode:
    def __init__(self, value):
        self.value = value

class VarAccessNode:
    def __init__(self, name):
        self.name = name

class OutputNode:
    def __init__(self, value):
        self.value = value  # This can be a StringNode or IdentifierNode



# INTERPRETER  

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
    
    def visit_OutputNode(self, node):
        value = self.visit(node.value)
        print(f'{value}') 

    def visit_StringNode(self, node):
        return node.value

    def visit_VarAccessNode(self, node):
        if node.name in self.variables:
            return self.variables[node.name]
        else:
            raise NameError(f"Variable '{node.name}' is not defined")

parser = Parser(tokens)
ast_nodes = parser.parse_statements()

interpreter = Interpreter()
for node in ast_nodes:
    interpreter.visit(node)

print(interpreter.variables)