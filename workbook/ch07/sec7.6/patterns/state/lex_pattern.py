#!/usr/bin/env python3

# Lexical Analyzer using the State Pattern
# Python implementation of the lexical analyzer using the State design pattern


from enum import Enum, auto
from typing import List, Dict, Optional, Tuple, Set
from abc import ABC, abstractmethod


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
        return f"{self.type.name:<15} {self.text:<25} {self.line:<10} {self.column:<10}"


class Lexer:
    def __init__(self, input_text: str):
        self.input = input_text
        self.position = 0
        self.line = 1
        self.column = 1
        self.current = input_text[0] if input_text else '\0'
        self.token_buffer = ""
        # set by the LexerContext
        self.state = None
    
    def advance_char(self) -> None:
        """Move to the next character in the input stream"""
        if self.current == '\0':
            return

        if self.current == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1
        self.current = self.input[self.position] if self.position < len(self.input) else '\0'
    
    def peek_next_char(self) -> str:
        """Look at the next character without advancing"""
        next_pos = self.position + 1
        return self.input[next_pos] if next_pos < len(self.input) else '\0'
    
    def add_to_buffer(self) -> None:
        """Add current character to token buffer"""
        self.token_buffer += self.current
    
    def reset_buffer(self) -> None:
        """Clear the token buffer"""
        self.token_buffer = ""
    
    def get_buffer(self) -> str:
        """Get the current token buffer content"""
        return self.token_buffer


class LexerState(ABC):
    """Abstract base class for all lexer states"""
    
    @abstractmethod
    def process(self, lexer: Lexer, context: 'LexerContext') -> Optional[Token]:
        """Process current character and transition to next state if needed"""
        pass


class LexerContext:
    """Context class that holds the current state and delegates processing to it"""
    
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        # initial state
        self.state = StartState()
        self.lexer.state = self.state
    
    def change_state(self, new_state: LexerState) -> None:
        """Change to a new state"""
        self.state = new_state
        self.lexer.state = new_state
    
    def process(self) -> Optional[Token]:
        """Process the current character using the active state"""
        return self.state.process(self.lexer, self)


class StartState(LexerState):
    """Initial state for the lexer"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current.isspace():
            lexer.add_to_buffer()
            token = Token(TokenType.WHITESPACE, lexer.get_buffer(), lexer.line, lexer.column)
            lexer.advance_char()
            lexer.reset_buffer()
            return token
            
        elif lexer.current.isalpha() or lexer.current == '_':
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(IdentifierState())
            
        elif lexer.current.isdigit():
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(NumberState())
            
        elif lexer.current == '"':
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(StringState())
            
        elif lexer.current == '/' and lexer.peek_next_char() == '/':
            lexer.add_to_buffer()
            lexer.advance_char()
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(CommentLineState())
            
        elif lexer.current == '/' and lexer.peek_next_char() == '*':
            lexer.add_to_buffer()
            lexer.advance_char()
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(CommentBlockState())
            
        elif lexer.current in "+-*/=<>!&|%^~?:":
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(OperatorState())
            
        elif lexer.current in ".,;()[]{}":
            lexer.add_to_buffer()
            token = Token(TokenType.DELIMITER, lexer.get_buffer(), lexer.line, lexer.column)
            lexer.advance_char()
            lexer.reset_buffer()
            return token
            
        elif lexer.current == '\0':
            return Token(TokenType.EOF, "EOF", lexer.line, lexer.column)
            
        else:
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(ErrorState())
            
        return None


class IdentifierState(LexerState):
    """State for processing identifiers and keywords"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current.isalnum() or lexer.current == '_':
            lexer.add_to_buffer()
            lexer.advance_char()
            return None
        else:
            # token complete
            buffer = lexer.get_buffer()
            token_type = TokenType.KEYWORD if buffer in KEYWORDS else TokenType.IDENTIFIER
            token = Token(token_type, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
            lexer.reset_buffer()
            context.change_state(StartState())
            return token


class NumberState(LexerState):
    """State for processing numeric literals"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current.isdigit():
            lexer.add_to_buffer()
            lexer.advance_char()
            return None
        elif lexer.current == '.':
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(NumberDotState())
            return None
        else:
            # integer number complete
            buffer = lexer.get_buffer()
            token = Token(TokenType.NUMBER, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
            lexer.reset_buffer()
            context.change_state(StartState())
            return token


class NumberDotState(LexerState):
    """State for processing the dot in a number"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current.isdigit():
            lexer.add_to_buffer()
            lexer.advance_char()
            context.change_state(NumberFloatState())
            return None
        else:
            # Error: dot not followed by digit
            context.change_state(ErrorState())
            return None


class NumberFloatState(LexerState):
    """State for processing floating point numbers"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current.isdigit():
            lexer.add_to_buffer()
            lexer.advance_char()
            return None
        else:
            # Float number is complete
            buffer = lexer.get_buffer()
            token = Token(TokenType.NUMBER, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
            lexer.reset_buffer()
            context.change_state(StartState())
            return token


class StringState(LexerState):
    """State for processing string literals"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current == '"':
            # close string
            lexer.add_to_buffer()
            buffer = lexer.get_buffer()
            token = Token(TokenType.STRING, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
            lexer.advance_char()
            lexer.reset_buffer()
            context.change_state(StartState())
            return token
        elif lexer.current == '\0' or lexer.current == '\n':
            # unterminated string
            context.change_state(ErrorState())
            return None
        else:
            lexer.add_to_buffer()
            lexer.advance_char()
            return None


class CommentLineState(LexerState):
    """State for processing single-line comments"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current == '\n' or lexer.current == '\0':
            # end of comment
            buffer = lexer.get_buffer()
            token = Token(TokenType.COMMENT, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
            if lexer.current == '\n':
                lexer.advance_char()
            lexer.reset_buffer()
            context.change_state(StartState())
            return token
        else:
            lexer.add_to_buffer()
            lexer.advance_char()
            return None


class CommentBlockState(LexerState):
    """State for processing multi-line comments"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        if lexer.current == '*' and lexer.peek_next_char() == '/':
            # end of block comment
            lexer.add_to_buffer()
            lexer.advance_char()
            lexer.add_to_buffer()
            buffer = lexer.get_buffer()
            token = Token(TokenType.COMMENT, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
            lexer.advance_char()
            lexer.reset_buffer()
            context.change_state(StartState())
            return token
        elif lexer.current == '\0':
            # unterminated comment
            context.change_state(ErrorState())
            return None
        else:
            lexer.add_to_buffer()
            lexer.advance_char()
            return None


class OperatorState(LexerState):
    """State for processing operators"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        buffer = lexer.get_buffer()
        # check for two-character operators
        if (len(buffer) == 1 and
            ((buffer[0] == '+' and lexer.current == '+') or
             (buffer[0] == '-' and lexer.current == '-') or
             (buffer[0] == '=' and lexer.current == '=') or
             (buffer[0] == '!' and lexer.current == '=') or
             (buffer[0] == '<' and lexer.current == '=') or
             (buffer[0] == '>' and lexer.current == '=') or
             (buffer[0] == '&' and lexer.current == '&') or
             (buffer[0] == '|' and lexer.current == '|'))):
            lexer.add_to_buffer()
            lexer.advance_char()
            
        # operator token is complete
        buffer = lexer.get_buffer()
        token = Token(TokenType.OPERATOR, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
        lexer.reset_buffer()
        context.change_state(StartState())
        return token


class ErrorState(LexerState):
    """State for handling errors"""
    
    def process(self, lexer: Lexer, context: LexerContext) -> Optional[Token]:
        buffer = lexer.get_buffer()
        token = Token(TokenType.ERROR, buffer, lexer.line - (buffer.count('\n')), lexer.column - len(buffer))
        lexer.reset_buffer()
        context.change_state(StartState())
        return token


def tokenize(source_code: str) -> List[Token]:
    """Tokenize the given source code and return all tokens"""
    lexer = Lexer(source_code)
    context = LexerContext(lexer)
    tokens = []
    
    while True:
        token = context.process()
        if token:
            if token.type != TokenType.WHITESPACE:  # skip whitespace by default
                tokens.append(token)
            if token.type == TokenType.EOF:
                break
    
    return tokens


def main():
    source_code = """int main() {
    int x = 42;
    return x;
}"""

    tokens = tokenize(source_code)
    
    print("Tokens:")
    print(f"{'TYPE':<15} {'TEXT':<25} {'LINE':<10} {'COLUMN':<10}")
    print("-" * 63)
    
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
