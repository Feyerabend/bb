

## Lexer State Diagram

```mermaid
stateDiagram-v2
    [*] --> STATE_START

    STATE_START --> STATE_IDENTIFIER: letter/_ 
    STATE_START --> STATE_NUMBER: digit
    STATE_START --> STATE_STRING: '"'
    STATE_START --> STATE_COMMENT_LINE: "//"
    STATE_START --> STATE_COMMENT_BLOCK: "/*"
    STATE_START --> STATE_OPERATOR: +-*/=<>!&|%^~?:
    STATE_START --> STATE_START: delimiter
    STATE_START --> STATE_START: whitespace
    STATE_START --> STATE_ERROR: invalid char

    STATE_IDENTIFIER --> STATE_IDENTIFIER: letter/digit/_
    STATE_IDENTIFIER --> STATE_START: other (emit TOKEN_IDENTIFIER/KEYWORD)

    STATE_NUMBER --> STATE_NUMBER: digit
    STATE_NUMBER --> STATE_NUMBER_DOT: '.'
    STATE_NUMBER --> STATE_START: non-digit (emit TOKEN_NUMBER)

    STATE_NUMBER_DOT --> STATE_NUMBER_FLOAT: digit
    STATE_NUMBER_DOT --> STATE_ERROR: non-digit

    STATE_NUMBER_FLOAT --> STATE_NUMBER_FLOAT: digit
    STATE_NUMBER_FLOAT --> STATE_START: non-digit (emit TOKEN_NUMBER)

    STATE_STRING --> STATE_STRING: any char except '"' or newline
    STATE_STRING --> STATE_START: '"' (emit TOKEN_STRING)
    STATE_STRING --> STATE_ERROR: newline/EOF

    STATE_COMMENT_LINE --> STATE_COMMENT_LINE: any char except newline
    STATE_COMMENT_LINE --> STATE_START: newline/EOF (emit TOKEN_COMMENT)

    STATE_COMMENT_BLOCK --> STATE_COMMENT_BLOCK: any char except '*'
    STATE_COMMENT_BLOCK --> STATE_START: '*/' (emit TOKEN_COMMENT)
    STATE_COMMENT_BLOCK --> STATE_ERROR: EOF

    STATE_OPERATOR --> STATE_OPERATOR: possible multi-char op (e.g., ++, ==)
    STATE_OPERATOR --> STATE_START: complete (emit TOKEN_OPERATOR)

    STATE_ERROR --> STATE_START: (emit TOKEN_ERROR)
```
