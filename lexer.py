# Basic lexer for the H language. 
# Uses RE for regular expression
import re
import ply.lex as lex

# Basic Tokens for setting a variable
tokens = [
    'SET',
    'OUTPUT',
    'IDENTIFIER',
    'EQUAL',
    'NUMBER',
    'STRING'
]

# Stored output
output = []

# Regex for each token
reserved = {
    'set': 'SET',
    'output': 'OUTPUT'
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

# Regex for ignored characters. (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule 
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
with open('main.htb', 'r') as f:
    data = f.read()

# Build the lexer
lexer = lex.lex()

# Give the lexer some input
lexer.input(data)

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)