
## Parsers Overview

Production rules are the formal constructs in a grammar that define the syntactic structure of a language.
They specify how symbols in the language can be generated or replaced during parsing. Each production rule
maps a non-terminal symbol to a sequence of terminal and/or non-terminal symbols, describing a valid
transformation within the grammar.

The general form of a production rule is:

```text
   A → α
```

Here, `A` is a non-terminal symbol (representing a syntactic category), and `α` is a sequence of terminals
(actual symbols of the language) and/or non-terminals (further rules). The left-hand side (`A`) indicates
what is being defined, and the right-hand side (`α`) specifies how it can be expanded.

For example, in a grammar for simple arithmetic expressions:

```text
    Expr → Expr + Term
    Expr → Term
    Term → Number
    Number → 0 | 1 | 2 | ... | 9
```

These rules define how complex expressions like `3 + 5` can be decomposed into their basic components
(numbers, operators) and parsed accordingly.



### Top-Down Parsers

These parsers start from the start symbol of the grammar and attempt to derive the input string by applying production rules.
1. LL Parsers:
    - The abbreviation stands for `Left-to-right parsing, Leftmost derivation`.
	- They process the input from left to right and produce a leftmost derivation of the input string.
	- LL(k): This means the parser looks ahead k tokens to make decisions.
	- LL(1): The most common variant where only one token of lookahead is used.
	- Works well for grammars without ambiguity, left recursion, or significant ambiguity in production choices.
	- Recursive Descent Parsers (discussed further below) are typically implemented as LL(1) parsers.

2. Recursive Descent Parsing:
	- A simple top-down parsing method where each non-terminal in the grammar is implemented as a recursive function.
	- Relies on LL(1) grammar for correctness.
	- It’s intuitive and easy to implement but requires that the grammar avoids left recursion and excessive ambiguity.

3. Predictive Parsing:
	- A non-recursive approach to LL parsing that uses a predictive table to guide parsing decisions.
	- Efficient for LL(1) grammars and avoids the need for recursive calls.


### Bottom-Up Parsers

These parsers start with the input tokens and attempt to reconstruct the start symbol of the grammar by reversing derivations.
1. LR Parsers:
	- The abbreviation stands for `Left-to-right parsing, Rightmost derivation in reverse`.
	- They process the input from left to right and construct a parse tree for a rightmost derivation in reverse.
	- Suitable for a broader class of grammars compared to LL parsers.

2. LR Variants:
	- SLR (Simple LR): Simplifies parsing by using a basic lookahead to resolve conflicts but works for a restricted set of grammars.
	- LALR (Lookahead LR): Combines states with identical cores to create a smaller parsing table, making it more memory-efficient
      than LR(1) while still supporting most programming language grammars.
	- LR(1): Uses a single lookahead token, supports a wide range of grammars, but parsing tables can become large.
	- GLR (Generalized LR): Handles non-deterministic or ambiguous grammars using parallel parsing paths.

3. Operator-Precedence Parsers:
	- A specific kind of bottom-up parser used for grammars where the structure is defined by operator precedence rules.
	- Simpler than full LR parsers but limited to certain grammars.


### Other Parsing Techniques

1. Combinatorial Parsing:
	- A functional programming approach to parsing where parsers are functions that can be combined in modular ways to recognize grammar constructs.
	- Often implemented in languages like Haskell or Scala.
	- Elegant, flexible, and well-suited to highly modular or complex grammar constructs.
	- More commonly used in small domain-specific languages rather than general-purpose compilers due to potential inefficiency.
2. Earley Parser:
	- A general parsing technique for any context-free grammar.
    - Suitable for ambiguous grammars but slower compared to LL and LR parsers for regular use.
3. CYK Parser:
	- Uses a dynamic programming approach and works on grammars in Chomsky Normal Form (CNF).
	- Efficient for ambiguous grammars but impractical for hand-written parsers.

Focusing on LL(1), Recursive Descent, and Combinatorial Parsing

1. LL(1) Parsing:
	- Strengths: Easy to implement, efficient for simple grammars, and guarantees linear parsing time for LL(1) grammars.
	- Limitations: Cannot handle left-recursive or ambiguous grammars. Requires careful grammar design to fit LL(1) constraints.
	- Uses a parsing table for predictive parsing, where each cell indicates which production to apply based on the current input token and non-terminal.

2. Recursive Descent Parsing:
	- Implements each grammar rule as a function, where non-terminals are recursive calls.
	- Parsing decisions are guided by lookahead (one token ahead in LL(1)).
	- Direct and clear for grammar constructs, making it excellent for prototyping parsers.
	- Example: For grammar $S \to aA ,  A \to b$ you might write:

```python
def parse_S():
    match('a')
    parse_A()

def parse_A():
    match('b')
```

3. Combinatorial Parsing:
	- Constructs parsers as composable components.
	- Allows direct representation of grammar rules as high-level abstractions, improving readability and maintainability.
	- Often uses monads (in functional languages) to chain parsing computations.
	- Example in Haskell:
```haskell
expr = do { x <- term; char '+'; y <- term; return (x + y) }
```

Each of these parsing techniques has its strengths, making them suitable for different kinds of grammars and use cases.
While LL(1) and recursive descent are particularly effective for simple or handcrafted grammars, combinatorial parsing
excels in modularity and expressiveness, making it ideal for functional programming approaches.