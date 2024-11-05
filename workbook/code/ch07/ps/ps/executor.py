class Executor:
    def __init__(self, stack: 'Stack', env: 'Environment'):
        pass

    def execute(self, ast: ASTNode):
        pass

    def run_operator(self, operator: str, operands: list[any]) -> any:
        pass

    def evaluate_procedure(self, procedure: list[Token]):
        pass