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
