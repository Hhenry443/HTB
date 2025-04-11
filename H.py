# Basic lexer for the H language. 
import ply.lex as lex

tokens = (
    'IF',
    'OUTPUT',
    'FART',
    'SET',
    'STRING',
    'NUMBER',
    'TRUE',
    'FALSE',
    'IDENTIFIER',
    'EQUAL',
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE'
)

# Stored output
output = []

# Regex for each token
reserved = {
    'set': 'SET',
    'output': 'OUTPUT',
    'fart': 'FART',
    'true': 'TRUE',
    'false': 'FALSE',
    'if': 'IF'
}

def t_IDENTIFIER(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

t_EQUAL = r'='

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

def t_STRING(t):
    r'"[^"\n]*"'  # Double-quoted strings only
    t.value = t.value[1:-1]  # Remove the quotes from the value
    return t

def t_TRUE(t):
    r'TRUE'
    t.value = 'TRUE'
    return t

def t_FALSE(t):
    r'FALSE'
    t.value = 'FALSE'
    return t

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'


# Regex for ignored characters. (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule 
def t_error(t):
    t.lexer.skip(1)
    
with open('main.htb', 'r') as f:
    data = f.read()

# Build the lexer
lexer = lex.lex()

# Give the lexer some input
lexer.input(data)

from collections import namedtuple

LexToken = namedtuple('LexToken', ['type', 'value', 'lineno', 'lexpos'])

tokens = []

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    tokens.append(tok)

# PARSER

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
            elif tok_type == 'FART':
                statements.append(self.parse_fart())
            elif tok_type == 'IF':
                statements.append(self.parse_if())
            else:
                raise SyntaxError(f"Unexpected token type: {tok_type}")

        return statements

    def parse_statement(self):
        tok_type = self.current().type
        if tok_type == 'SET':
            return self.parse_var_assign()
        elif tok_type == 'OUTPUT':
            return self.parse_output()
        elif tok_type == 'FART':
            return self.parse_fart()
        elif tok_type == 'IF':
            return self.parse_if()
        else:
            raise SyntaxError(f"Unexpected token in statement: {tok_type}")
    
    def parse_if(self):
        self.match('IF')
        condition = self.parse_expression()
        self.match('LBRACE')  # Match {

        statements = []
        while self.current() and self.current().type != 'RBRACE':
            statements.append(self.parse_statement())

        self.match('RBRACE')  # Match }

        return IfNode(condition, statements)  # ← This was missing
    
    def parse_expression(self):
        node = self.parse_term()

        while self.current() and self.current().type in ('PLUS', 'MINUS', 'EQUAL'):
            op_token = self.current()
            self.advance()
            right = self.parse_term()  # This could be another term, or in this case, a boolean literal
            node = BinOpNode(node, op_token, right)

        return node


    def parse_term(self):
        node = self.parse_factor()

        while self.current() and self.current().type in ('MULTIPLY', 'DIVIDE'):
            op_token = self.current()
            self.advance()
            right = self.parse_factor()
            node = BinOpNode(node, op_token, right)

        return node

    def parse_factor(self):
        tok = self.current()

        if tok.type == 'NUMBER':
            self.advance()
            return NumberNode(tok.value)
        elif tok.type == 'STRING':
            self.advance()
            return StringNode(tok.value)
        elif tok.type == 'TRUE':
            self.advance()
            return BooleanNode(True)
        elif tok.type == 'FALSE':
            self.advance()
            return BooleanNode(False)
        elif tok.type == 'IDENTIFIER':
            self.advance()
            return VarAccessNode(tok.value)  # Return a node for variable access
        elif tok.type == 'LPAREN':
            self.advance()
            node = self.parse_expression()
            self.match('RPAREN')
            return node
        else:
            raise SyntaxError(f"Unexpected token in factor: {tok}")

    def parse_var_assign(self):
        self.match('SET')
        identifier_token = self.match('IDENTIFIER')
        self.match('EQUAL')  # Match '='

        value_node = self.parse_expression()  # <--- now parses arithmetic expressions

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

    def parse_fart(self):
        self.match('FART')
        tok = self.current()
        
        if tok.type == 'NUMBER':
            self.advance()
            return FartNode(NumberNode(tok.value))
        else:
            raise SyntaxError(f"Expected NUMBER after 'fart', got {tok}")
        
        
class VarAssignNode:
    def __init__(self, name, value):
        self.name = name      # e.g. 'x'
        self.value = value    # an AST node (like NumberNode)

    def __str__(self):
        return f"VarAssignNode(name={self.name}, value={self.value})"

class NumberNode:
    def __init__(self, value):
        self.value = value    # e.g. 5

    def __str__(self):
        return f"NumberNode(value={self.value})"

class StringNode:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"StringNode(value={self.value})"

class BooleanNode:
    def __init__(self, value):
        self.value = value  # True or False

    def __str__(self):
        return f"BooleanNode(value={self.value})"
    
class VarAccessNode:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"VarAccessNode(name={self.name})"

class OutputNode:
    def __init__(self, value):
        self.value = value  # This can be a StringNode or IdentifierNode

    def __str__(self):
        return f"OutputNode(value={self.value})"

class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left = left_node
        self.op = op_token
        self.right = right_node

    def __str__(self):
        return f"BinOpNode(left={self.left}, op={self.op}, right={self.right})"

class FartNode:
    def __init__(self, intensity):
        self.intensity = intensity
        
    def __str__(self):
        return f"FartNode(intensity={self.intensity})"

class IfNode:
    def __init__(self, condition, statements):
        self.condition = condition
        self.statements = statements  # List of statements now

    def __str__(self):
        return f"IfNode(condition={self.condition}, statements={[str(s) for s in self.statements]})"

    
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

    def visit_BooleanNode(self, node):
        return node.value
    
    def visit_VarAccessNode(self, node):
        if node.name in self.variables:
            return self.variables[node.name]
        else:
            raise NameError(f"Variable '{node.name}' is not defined")
        
    def visit_BinOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op.type

        if op == 'PLUS':
            return left + right
        elif op == 'MINUS':
            return left - right
        elif op == 'MULTIPLY':
            return left * right
        elif op == 'DIVIDE':
            return left / right
        elif op == 'EQUAL':
            return left == right
        else:
            raise Exception(f"Unknown operator {op}")

    def visit_FartNode(self, node):
        intensity = self.visit(node.intensity)
        output = 'br'
        for i in range(intensity):
            output = output + 'a'
        
        output = output + 'p'
        print(f'{output}')
        
    def visit_IfNode(self, node):
        condition_result = self.visit(node.condition)
        if condition_result:
            for statement in node.statements:
                self.visit(statement)


                
parser = Parser(tokens)
ast_nodes = parser.parse_statements()

interpreter = Interpreter()
for node in ast_nodes:
    interpreter.visit(node)

