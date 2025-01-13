
## Tokeniser, or Tokenizer, Lexer ..

__build__

```shell
make clean
make
make samples
```

This system tokenises input files from the samples directory and reads the tokenised output to display it.
Tokens are annotated with approximate locations in the source code. Although the grammar isn't applied yet,
the system makes a best-effort guess to identify reserved words, which are prohibited from being used as
anything else.

This code implements a simple tokeniser (lexer) for a programming language similar to PL/0 (some adjustments
have been made). The tokeniser reads a source file containing code, identifies individual tokens based on
language grammar, and writes these tokens to an output file.


### Overview

The tokeniser breaks down the input program into tokens, which are the smallest units of meaning in the
language (e.g. keywords, identifiers, numbers, operators). The tokens are written to an output file in
a readable format.

__nextChar()__

- Advances to the next character in the input string (sourceCode) and updates currentChar.
- Maintains the state of the tokeniser as it processes the input.

__skipWhitespace()__

- Skips over whitespace characters (' ', '\t', '\n', etc.).
- If a newline ('\n') is encountered, it writes an "ENDOFLINE" token to the output file, which is useful
  for handling line-sensitive constructs (e.g. error reporting indicating where the error can be found).

__handleIdentifier()__

- Processes identifiers and keywords.
- Reads a sequence of alphanumeric characters and underscores (_).
- Checks if the read string matches a keyword (e.g. call, begin) and emits the corresponding token. If not,
  it is treated as an identifier.

__handleNumber()__

- Handles numeric literals.
- Reads a sequence of digits and emits a "NUMBER" token with its value.

__tokeniser()__

- The main function that orchestrates tokenization.
- Iterates through the input string (sourceCode), categorizing each character or sequence of characters into tokens.
- Handles:
    - Identifiers and keywords using handleIdentifier.
	- Numbers using handleNumber.
	- Symbols and operators directly ('(', ')', '+', '-', etc.).
	- Multi-character operators like '<=' and ':='.
	- Writes tokens to the output file in a readable format.

__cleanup()__

- Closes the input and output files and frees dynamically allocated memory to avoid resource leaks.

__fromSourceToTokens()__

- Reads the source file into memory.
- Sets up the tokeniser and output file.
- Calls tokeniser() to perform the actual tokenization.
- Cleans up resources after tokenization.


### Notes

1. Keywords vs. Identifiers:
- Keywords are reserved words (such as 'if', 'while') that have special meanings in the language.
- Identifiers are user-defined names (such as variable or procedure names).
- handleIdentifier() differentiates these by comparing the read string to a list of known keywords.

2. Operators and Symbols:
- Single-character symbols (e.g. '+', '-', '*', '(', ')') are directly tokenised.
- Multi-character operators (e.g. '<=', ':=') are handled by checking the next character after encountering the first one.

3. Error Handling:
- If an unexpected character is encountered, an "ERROR" token is emitted, and the tokeniser moves to the next character.

4. End of Input:
- The input ends when currentChar is '\0' (null terminator).
- An "ENDOFFILE" token is emitted to signify the end of the program.


### Example

Input:

```pascal
const x = 10, y = 20;
var z;
procedure p;
begin
  z := x + y;
  if odd z then call p
end.
```

Output:

```
CONSTSYM IDENT x EQL NUMBER 10 COMMA IDENT y EQL NUMBER 20 SEMICOLON ENDOFLINE
VARSYM IDENT z SEMICOLON ENDOFLINE
PROCSYM IDENT p SEMICOLON ENDOFLINE
BEGINSYM ENDOFLINE
IDENT z BECOMES IDENT x PLUS IDENT y SEMICOLON ENDOFLINE
IFSYM ODDSYM IDENT z THENSYM CALLSYM IDENT p ENDOFLINE
ENDSYM PERIOD ENDOFLINE
ENDOFFILE
```

1. Input Processing:
- The input file is read into memory as a single string (sourceCode).
- The tokeniser processes the input one character at a time using nextChar().

2. Token Identification:
- Each character is categorized:
- Letters (a-z, A-Z, _) start identifiers or keywords.
- Digits (0-9) start numeric literals.
- Symbols (+, -, *, etc.) are matched directly.
- Multi-character tokens (<=, :=) are handled by peeking at the next character.

3. Output:
- Tokens are written to the output file in a readable format.


Code Improvements and Considerations
1. Memory Leaks:
- strdup() is used to duplicate strings, but the duplicates are not freed. Use free() after the token is written.

2. Error Handling:
- More informative error messages could be added.
- Include the line number in errors to make debugging easier.

3. Performance:
- For larger inputs, processing character-by-character can be slow. Using a buffered approach might improve performance.

4. Extensibility:
- Add support for additional tokens, like string literals, comments, or custom operators.


### Summary

This tokeniser is a simple implementation for a small programming language. It efficiently
classifies input characters into tokens while handling common constructs like identifiers,
keywords, numbers, and operators. It produces a tokenized representation of the input code,
which is an essential step before parsing and compiling.
