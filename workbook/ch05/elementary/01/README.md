
## Elementary: Compiling in Practice

We begin with a straightforward implementation of a [mini](MINI.md) compiler designed to handle basic
arithmetic expressions. This simple compiler serves as an introductory example, illustrating the fundamental
components of the compilation process. It encompasses key stages such as lexical analysis (tokenising
the input), parsing (building a syntax tree), semantic analysis (ensuring correctness of operations),
and code generation (translating the syntax tree into executable code). Despite its simplicity, the
mini compiler provides a hands-on foundation for understanding the core principles of compiler construction.

From this starting point, we can systematically build upon our knowledge and skills to tackle more advanced
and complex examples. A natural progression is to explore a more substantial compiler for the educational
programming language [PL/0](PL0.md). PL/0 is a well-known minimalist language often used for teaching compiler
construction. It introduces additional concepts like variable declarations, procedures, control flow
(such as loops and conditionals), and a more comprehensive symbol table for managing scopes and identifiers.

By transitioning from the mini compiler to PL/0, we expand our understanding of compiler design, delving
deeper into topics such as abstract syntax trees (ASTs), type checking (as we have only one it is minimal),
nested scopes, and procedural abstraction. Moreover, PL/0 provides an excellent platform to experiment
with optimisation techniques, error handling, and even extending the language's features. This incremental
approach allows learners to solidify their understanding of the compilation process while tackling
increasingly challenging problems in a structured and manageable way.

### Some changes

To begin our exploration of PL/0, we will make some modifications to its [grammar](GRAMMAR.md) to
better align it with modern programming practices and simplify its usage. The first change involves
removing the "odd" keyword. In the original grammar, the "odd" keyword was used within conditional
statements to evaluate whether a given numeric expression (on the right-hand side of the condition)
was odd or even. If the expression was odd, the condition would evaluate to true; otherwise, it
would evaluate to false. While this feature is an interesting aspect of the language, its utility
is limited, and removing it streamlines the grammar while reducing potential confusion for learners
encountering it for the first time.

The second adjustment introduces parentheses around conditions, similar to the convention used in
programming languages such as C. For instance, a condition in the original PL/0 might appear without
parentheses, whereas our modified grammar will require conditions to be enclosed within parentheses
e.g. '(x < y)'. This change not only makes the syntax more explicit and visually structured but also
aligns with the familiarity that many programmers already have with conditional syntax in widely-used
languages.

Finally, we adapt the handling of statement terminations by introducing semicolons (;) to mark the
end of statements rather than using them as separators. In the original PL/0, semicolons acted as
delimiters between consecutive statements, which differs from the more common convention of treating
semicolons as terminators. For example, instead of writing 'begin a := b; c := d end', the new grammar
would use 'begin a := b; c := d; end' with each semicolon clearly indicating the conclusion of a statement.
This adjustment simplifies the parsing process and aligns PL/0's syntax more closely with modern
programming languages, making it easier for students to grasp and work with.

These changes are not just superficial; they reflect deliberate design choices aimed at making the
language more intuitive and accessible while providing a better foundation for understanding compiler
construction. They also allow learners to focus on core concepts without being bogged down by
idiosyncrasies that may not translate to other programming environments.



### Tokenisation ...

### Parsing ..

### Analysis

### IR ..

### Code ..



