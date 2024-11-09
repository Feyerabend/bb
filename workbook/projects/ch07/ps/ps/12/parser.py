# parser.py
from lexer import Token, Lexer

class ASTNode:
    def __init__(self, type: str, value: any = None, children: list['ASTNode'] = None):
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return self.pretty_print(indent=0)
#       return f"ASTNode({self.type}, {self.value}, {self.children})"

    def pretty_print(self, indent=0):
        # indentation and node's type and value
        indent_str = ' ' * indent
        repr_str = f"{indent_str}ASTNode(type={self.type}, value={self.value})"

        # children, recursively pretty-print them with increased indentation
        if self.children:
            repr_str += '\n' + indent_str + '{'
            for child in self.children:
                repr_str += '\n' + child.pretty_print(indent + 4)  # indent for child nodes
            repr_str += '\n' + indent_str + '}'

        return repr_str

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def parse(self) -> ASTNode:
        instructions = []
        while self.index < len(self.tokens):
            instructions.append(self.parse_instruction())
        return ASTNode("Program", children=instructions)

    def parse_instruction(self) -> ASTNode:
        token = self._peek()
        
        if token.type == "NUMBER" or token.type == "STRING" or token.type == "NAME" or token.type == "COMMENT":
            return self._advance_and_wrap("Push")
        
        if token.value in {"add", "sub", "mul", "div", "dup", "exch", "pop", "def"}:
            return self._advance_and_wrap("Operator")
        
        if token.value in {"moveto", "lineto", "curveto", "closepath"}:
            return self.parse_path_command()

        if token.value in {"setcolor", "setlinewidth", "stroke", "fill"}:
            return self.parse_graphics_state_command()

        if token.value in {"dict", "begin", "end", "load", "store"}:
            return self.parse_dictionary_command()

        if token.value == "if" or token.value == "ifelse" or token.value == "repeat":
            return self.parse_control_structure()

        if token.type == "LBRACE":
            return self.parse_block()

        raise ValueError(f"Unexpected token: {token}")

    def parse_path_command(self) -> ASTNode:
        command = self._advance().value
        if command == "moveto" or command == "lineto":
            return ASTNode("PathCommand", command, [self.parse_number(), self.parse_number()])
        elif command == "curveto":
            return ASTNode("PathCommand", command, [
                self.parse_number(), self.parse_number(),
                self.parse_number(), self.parse_number(),
                self.parse_number(), self.parse_number()
            ])
        elif command == "closepath":
            return ASTNode("PathCommand", command)

    def parse_graphics_state_command(self) -> ASTNode:
        command = self._advance().value
        if command == "setcolor":
            return ASTNode("GraphicsStateCommand", command, [
                self.parse_number(), self.parse_number(), self.parse_number()
            ])
        elif command == "setlinewidth":
            return ASTNode("GraphicsStateCommand", command, [self.parse_number()])
        else:
            return ASTNode("GraphicsStateCommand", command)

    def parse_dictionary_command(self) -> ASTNode:
        command = self._advance().value
        if command == "dict":
            return ASTNode("DictionaryCommand", command, [self.parse_number()])
        elif command == "load" or command == "store":
            return ASTNode("DictionaryCommand", command, [self.parse_name()])
        else:
            return ASTNode("DictionaryCommand", command)

    def parse_control_structure(self) -> ASTNode:
        command = self._advance().value
        if command == "if":
            return ASTNode("ControlStructure", command, [self.parse_block()])
        elif command == "ifelse":
            return ASTNode("ControlStructure", command, [
                self.parse_block(), self.parse_block()
            ])
        elif command == "repeat":
            return ASTNode("ControlStructure", command, [
                self.parse_number(), self.parse_block()
            ])

    def parse_block(self) -> ASTNode:
        self._expect("LBRACE")
        instructions = []
        while self._peek().type != "RBRACE":
            instructions.append(self.parse_instruction())
        self._expect("RBRACE")
        return ASTNode("Block", children=instructions)

    def parse_number(self) -> ASTNode:
        token = self._expect("NUMBER")
        return ASTNode("Number", token.value)

    def parse_name(self) -> ASTNode:
        token = self._expect("NAME")
        return ASTNode("Name", token.value)

    def parse_name(self) -> ASTNode:
        token = self._expect("COMMENT")
        return ASTNode("Comment", token.value)

    def _peek(self) -> Token:
        return self.tokens[self.index]

    def _advance(self) -> Token:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def _advance_and_wrap(self, node_type: str) -> ASTNode:
        token = self._advance()
        return ASTNode(node_type, token.value)

    def _expect(self, type: str) -> Token:
        token = self._advance()
        if token.type != type:
            raise ValueError(f"Expected token type {type} but got {token.type}")
        return token
