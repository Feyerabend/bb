
## Syntax: Tokeniser, or Tokenizer, Lexer .. with annotations

__Build__

```shell
make clean
make
make samples
```

This system tokenises input files from the samples directory and reads the tokenised output to display it.
Tokens are *annotated* with approximate locations in the source code. Although the grammar isn't applied yet,
the system makes a best-effort guess to identify reserved words, which are prohibited from being used as
anything else.

This code implements a simple tokeniser (lexer) for a programming language similar to PL/0 (some adjustments
have been made). The tokeniser reads a source file containing code, identifies individual tokens based on
language grammar, and writes these tokens to an output file.

### Project

The aim of this project is to build a flexible and robust tokeniser for a simple programming language. The tokeniser will:

1. Identify Tokens: Recognise identifiers, numbers, keywords, operators, delimiters, and other syntactic components.

2. Annotate Locations: Attach precise location metadata (e.g., line and column numbers) to each token to facilitate debugging.

3. Handle Errors: Detect invalid tokens, highlight their location, and provide meaningful annotations to help the user
   understand and correct mistakes.

4. Suggest Corrections: For errors such as misspelled keywords or invalid identifiers, the system will offer suggestions
   or guesses for what might have been intended.


#### Features

1. Token Analysis:
	- Reserved keywords are checked and validated.
	- Identifiers and constants are recognised according to lexical rules.
	- Errors are marked when tokens deviate from expectations.
2. Error Detection and Annotation:
	- Invalid tokens are flagged with precise locations.
	- Error messages describe the issue and possible causes.
	- The system attempts to suggest corrections for misspellings or unintended usage.
3. Suggestions:
	- For misspelled keywords, the system provides likely matches using string similarity measures.
	- For misplaced tokens, suggestions are made based on contextual rules.
4. Extensibility:
	- Built with modularity to allow integration with parsers.
	- Easily adjustable for other PL/0-like languages or entirely new grammars.


#### Workflow

1. Input Source File: A '.pas' file containing source code is provided as input.

2. Tokenisation:
	- The tokeniser scans the input line by line.
	- Tokens are extracted based on regular expressions and language rules.

3. Error Handling:
	- If a token cannot be matched, it is marked as an error.
	- Annotations include the token’s location and a descriptive error message.

4. Output:
	- The tokenised output is saved to a file, with errors and suggestions highlighted for easy debugging.


#### Challenges and Solutions

1. Handling Ambiguities:
	- Challenge: Similar-looking tokens or partial matches may cause confusion.
	- Solution: Use greedy matching and backtracking to ensure the longest valid token is selected.

2.	Providing Useful Suggestions:
	- Challenge: Generating accurate guesses for misspelled keywords.
	- Solution: Implement a string similarity algorithm (e.g. Levenshtein distance).

3.	Annotating Errors Precisely:
	- Challenge: Maintaining accurate line and column counts during tokenisation.
	- Solution: Include metadata updates for every scanned character.

__Roadmap__

1: Implement the basic tokeniser with annotation support. DONE.

2: Add error detection and basic correction suggestions.

3: Extend to handle more complex language features and integrate with a parser.

4: Optimise for performance and release a production-ready version.

__Implementation Languages__

- *Python*: Ideal for rapid development, string manipulation, and prototyping error-detection features.
- *JavaScript*: Suitable for browser-based tokenisation tools, illustrating process or integrating into web development workflows.
- *C*: Provides performance benefits for large-scale or production-grade systems, especially in embedded environments.
