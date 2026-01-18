#!/usr/bin/env python3

# Lexical Analyzer State Machine
# Python implementation of the C lexical analyser in state machine style.


from enum import Enum, auto
from typing import List, Dict, Optional, Tuple


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    COMMENT = auto()
    WHITESPACE = auto()
    ERROR = auto()
    EOF = auto()


class LexerState(Enum):
    START = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    NUMBER_DOT = auto()
    NUMBER_FLOAT = auto()
    STRING = auto()
    COMMENT_LINE = auto()
    COMMENT_BLOCK = auto()
    OPERATOR = auto()
    ERROR = auto()


MAX_TOKEN_LENGTH = 128

KEYWORDS = [
    "if", "else", "while", "for", "return", "int", "float",
    "char", "void", "struct", "break", "continue"
]


class Token:
    def __init__(self, type: TokenType, text: str, line: int, column: int):
        self.type = type
        self.text = text
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"{token_type_to_string(self.type):<15} {self.text:<25} {self.line:<10} {self.column:<10}"


class Lexer:
    def __init__(self, input_text: str):
        self.input = input_text
        self.position = 0
        self.line = 1
        self.column = 1
        self.state = LexerState.START
        self.current = input_text[0] if input_text else '\0'

    def advance_char(self) -> None:
        if self.current == '\0':
            return

        if self.current == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1
        self.current = self.input[self.position] if self.position < len(self.input) else '\0'


def is_keyword(text: str) -> bool:
    return text in KEYWORDS


def token_type_to_string(type: TokenType) -> str:
    return type.name


def get_next_token(lexer: Lexer) -> Token:
    token = Token(TokenType.ERROR, "", lexer.line, lexer.column)
    length = 0
    token_complete = False

    while not token_complete and lexer.current != '\0':
        if length >= MAX_TOKEN_LENGTH - 1:
            token.text = "TOO_LONG"
            token.type = TokenType.ERROR
            return token

        if lexer.state == LexerState.START:
            if lexer.current.isspace():
                token.type = TokenType.WHITESPACE
                token.text = lexer.current
                lexer.advance_char()
                token_complete = True
            elif lexer.current.isalpha() or lexer.current == '_':
                lexer.state = LexerState.IDENTIFIER
                token.text = lexer.current
                lexer.advance_char()
            elif lexer.current.isdigit():
                lexer.state = LexerState.NUMBER
                token.text = lexer.current
                lexer.advance_char()
            elif lexer.current == '"':
                lexer.state = LexerState.STRING
                token.text = lexer.current
                lexer.advance_char()
            elif lexer.current == '/' and lexer.position + 1 < len(lexer.input) and lexer.input[lexer.position + 1] == '/':
                lexer.state = LexerState.COMMENT_LINE
                token.text = lexer.current
                lexer.advance_char()
                token.text += lexer.current
                lexer.advance_char()
            elif lexer.current == '/' and lexer.position + 1 < len(lexer.input) and lexer.input[lexer.position + 1] == '*':
                lexer.state = LexerState.COMMENT_BLOCK
                token.text = lexer.current
                lexer.advance_char()
                token.text += lexer.current
                lexer.advance_char()
            elif lexer.current in "+-*/=<>!&|%^~?:":
                lexer.state = LexerState.OPERATOR
                token.text = lexer.current
                lexer.advance_char()
            elif lexer.current in ".,;()[]{}":
                token.type = TokenType.DELIMITER
                token.text = lexer.current
                lexer.advance_char()
                token_complete = True
            else:
                lexer.state = LexerState.ERROR
                token.text = lexer.current
                lexer.advance_char()

        elif lexer.state == LexerState.IDENTIFIER:
            if lexer.current.isalnum() or lexer.current == '_':
                token.text += lexer.current
                lexer.advance_char()
            else:
                token.type = TokenType.KEYWORD if is_keyword(token.text) else TokenType.IDENTIFIER
                token_complete = True
                lexer.state = LexerState.START

        elif lexer.state == LexerState.NUMBER:
            if lexer.current.isdigit():
                token.text += lexer.current
                lexer.advance_char()
            elif lexer.current == '.':
                token.text += lexer.current
                lexer.state = LexerState.NUMBER_DOT
                lexer.advance_char()
            else:
                token.type = TokenType.NUMBER
                token_complete = True
                lexer.state = LexerState.START

        elif lexer.state == LexerState.NUMBER_DOT:
            if lexer.current.isdigit():
                token.text += lexer.current
                lexer.state = LexerState.NUMBER_FLOAT
                lexer.advance_char()
            else:
                lexer.state = LexerState.ERROR

        elif lexer.state == LexerState.NUMBER_FLOAT:
            if lexer.current.isdigit():
                token.text += lexer.current
                lexer.advance_char()
            else:
                token.type = TokenType.NUMBER
                token_complete = True
                lexer.state = LexerState.START

        elif lexer.state == LexerState.STRING:
            if lexer.current == '"':
                token.text += lexer.current
                token.type = TokenType.STRING
                token_complete = True
                lexer.advance_char()
                lexer.state = LexerState.START
            elif lexer.current == '\0' or lexer.current == '\n':
                lexer.state = LexerState.ERROR
            else:
                token.text += lexer.current
                lexer.advance_char()

        elif lexer.state == LexerState.COMMENT_LINE:
            if lexer.current == '\n' or lexer.current == '\0':
                token.type = TokenType.COMMENT
                token_complete = True
                if lexer.current == '\n':
                    lexer.advance_char()
                lexer.state = LexerState.START
            else:
                token.text += lexer.current
                lexer.advance_char()

        elif lexer.state == LexerState.COMMENT_BLOCK:
            if lexer.current == '*' and lexer.position + 1 < len(lexer.input) and lexer.input[lexer.position + 1] == '/':
                token.text += lexer.current
                lexer.advance_char()
                token.text += lexer.current
                token.type = TokenType.COMMENT
                token_complete = True
                lexer.advance_char()
                lexer.state = LexerState.START
            elif lexer.current == '\0':
                lexer.state = LexerState.ERROR
            else:
                token.text += lexer.current
                lexer.advance_char()

        elif lexer.state == LexerState.OPERATOR:
            if (len(token.text) == 1 and
                ((token.text[0] == '+' and lexer.current == '+') or
                 (token.text[0] == '-' and lexer.current == '-') or
                 (token.text[0] == '=' and lexer.current == '=') or
                 (token.text[0] == '!' and lexer.current == '=') or
                 (token.text[0] == '<' and lexer.current == '=') or
                 (token.text[0] == '>' and lexer.current == '=') or
                 (token.text[0] == '&' and lexer.current == '&') or
                 (token.text[0] == '|' and lexer.current == '|'))):
                token.text += lexer.current
                lexer.advance_char()
            token.type = TokenType.OPERATOR
            token_complete = True
            lexer.state = LexerState.START

        elif lexer.state == LexerState.ERROR:
            token.type = TokenType.ERROR
            token_complete = True
            lexer.state = LexerState.START

    if lexer.current == '\0' and not token_complete:
        token.type = TokenType.EOF
        token.text = "EOF"

    return token


def main():
    source_code = """int main() {
    int x = 42;
    return x;
}"""

    lexer = Lexer(source_code)

    print("Tokens:")
    print(f"{'TYPE':<15} {'TEXT':<25} {'LINE':<10} {'COLUMN':<10}")
    print("-" * 63)

    while True:
        token = get_next_token(lexer)
        if token.type != TokenType.WHITESPACE:
            print(token)
        if token.type == TokenType.EOF:
            break


if __name__ == "__main__":
    main()