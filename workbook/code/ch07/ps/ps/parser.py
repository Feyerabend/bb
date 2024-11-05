class ASTNode:
    def __init__(self, type: str, value: any, children: list['ASTNode'] = None):
        pass

class Parser:
    def __init__(self, tokens: list[Token]):
        pass

    def parse(self) -> ASTNode:
        pass

    def parse_expression(self, tokens: list[Token]) -> ASTNode:
        pass