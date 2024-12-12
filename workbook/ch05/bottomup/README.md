
## Bottom-Up Parsing

Bottom-up parsing is a type of syntactic analysis technique used to recognize a language by starting with the input symbols (the "leaves") and progressively reducing them to the start symbol of the grammar. Unlike top-down parsing (which begins with the start symbol and works its way down to the leaves), bottom-up parsing works by attempting to find the deepest derivations first and then reducing the string to match the start symbol.

1. Shift and Reduce Operations:
- Shift: This operation moves the next input symbol onto the stack. The stack initially starts empty, and the shift operation gradually builds up the structure of the input.
- Reduce: Once the parser has built up enough symbols in the stack, it checks if a sequence of symbols matches a right-hand side of a production rule in the grammar. If a match is found, the parser "reduces" this sequence of symbols to the corresponding non-terminal (left-hand side) of the rule.

2. Handles and Handles Recognition:
A handle is a substring of the input that matches the right-hand side of a production rule in the grammar. The idea behind bottom-up parsing is that the parser attempts to identify and reduce these handles until the start symbol is derived.

3. Shift-Reduce Conflicts:
Sometimes, a bottom-up parser might face situations where it's unclear whether to shift or reduce. This is called a shift-reduce conflict. In practical implementations (like in certain parser generators), this can be resolved by prioritizing one action over the other.

4. Final Goal:
The goal of bottom-up parsing is to reduce the entire input string to the start symbol. If successful, this means the input string is a valid sentence in the language defined by the grammar.


### Process

Bottom-up parsing works by applying reductions and shifts in the following steps:
- Start with the input symbols (tokens) from left to right.
- Shift the tokens onto the stack. This means pushing the tokens from the input onto the stack one by one.
- After each shift, check the top of the stack to see if it matches the right-hand side of any production rule in the grammar. If a match is found, perform a reduce operation, which involves replacing the matched symbols with the left-hand side (non-terminal) of the rule.
- Repeat the process: Shift tokens and reduce as possible. The process continues until the stack contains only the start symbol of the grammar.


#### Why?
- Efficient for LR Parsers: Bottom-up parsing is often used in LR parsers, which are efficient for a wide range of programming languages and grammars. These parsers can handle context-free grammars (CFG) with relatively simple deterministic strategies.
- Handles Complex Expressions: This approach naturally handles complex expressions in programming languages, such as arithmetic operations, control structures (like if-else or loops), and others.


### Example: POP3 

This program implements a *bottom-up parser* using a *shift-reduce parsing* approach to process a simplified grammar for input commands. It includes two main components: a tokenizer and a parser.

#### Tokenizer
The tokenizer converts the raw input string into a sequence of tokens based on predefined patterns (regular expressions). Each token represents a syntactic unit like a command, number, or string. 

Purpose of the tokenizer
* Breaks down input into manageable, discrete units.
* Removes unnecessary elements, such as whitespace.
* Classifies each unit with a type (e.g., `COMMAND`, `NUMBER`, `STRING`).

Given input:
> USER 1234\nPASS secret\n

Produce:
```python
[
    ('COMMAND', 'USER'),
    ('NUMBER', '1234'),
    ('NEWLINE', '\n'),
    ('COMMAND', 'PASS'),
    ('STRING', 'secret'),
    ('NEWLINE', '\n')
]
```

#### Parser

The `ShiftReduceParser` processes tokens using the *shift-reduce strategy*:

### Phases:
- *Shift*: Push the next token from the input onto a stack.
- *Reduce*: Apply production rules if the top elements of the stack match a rule's right-hand side.

### Production Rules:
- *Rule 1*: $\( S \rightarrow \text{COMMAND NUMBER} \)$ (a `COMMAND` followed by a `NUMBER` is reduced to `S`).
- *Rule 2*: $\( S \rightarrow \text{COMMAND STRING} \)$ (a `COMMAND` followed by a `STRING` is reduced to `S`).
- *Rule 3*: $\( S \rightarrow SS \)$ (two `S` elements are reduced to a larger `S`, combining them).

### Example Workflow:
For the input tokens:

```python
[
    ('COMMAND', 'USER'),
    ('NUMBER', '1234'),
    ('NEWLINE', '\n'),
    ('COMMAND', 'PASS'),
    ('STRING', 'secret'),
    ('NEWLINE', '\n')
]
```

1. The parser shifts `('COMMAND', 'USER')` and `('NUMBER', '1234')`, then applies Rule 1 to reduce them to `S`.
2. It shifts `('COMMAND', 'PASS')` and `('STRING', 'secret')`, then applies Rule 2 to reduce them to another `S`.
3. Finally, Rule 3 combines the two `S` elements into a single `S`, completing the parse.

#### Parse Tree

The final parse tree reflects the hierarchical structure of the input:

```python
[
    ('S', [('NUMBER', '1234'), ('COMMAND', 'USER')]),
    ('S', [('STRING', 'secret'), ('COMMAND', 'PASS')]),
    ('S', [
        ('S', [('STRING', 'secret'), ('COMMAND', 'PASS')]),
        ('S', [('NUMBER', '1234'), ('COMMAND', 'USER')])
    ])
]
```

This structure is derived from the application of production rules and represents the parsed input.
