
## Virtual Machines and Syntax Parsing

Here we will explore a practical approach to syntax analysis by implementing a virtual machine
that processes input characters or tokens. The machine simulates a tape-based mechanism:
an input "tape" for feeding the system data and an output "tape" for storing results.
The machine matches expected characters and executes predefined actions based on a program's
logic. This simple model serves as an illustration of text parsing and token manipulation.


### Production Rules

The concept of production rules, widely used in parsing and other domains like expert systems,
is central to this exploration. Regard an example of a simple set of production rules:

```text
  S → A B
  A → a | ac
  B → b | cb
```

From this we can generate a limited set of "products".

```text
  S → AB →  aB →   ab
  S → AB →  aB →  acb
  S → AB → acB →  acb
  S → AB → acB → accb
```

Each step involves substituting placeholders (uppercase letters) with terminal symbols
(lowercase letters) according to the defined rules.


## The Metcalfe Machine

The Metcalfe machine[^metcalfe] operates using a minimalistic instruction set designed for token
matching, conditional branching, and output generation. The instructions include:

__call &lt;label&gt;__
: Push current position of input and output on a stack.
Call some subprogram/-routine at label (possibly recursive calls).

__false &lt;label&gt;__
: Conditional jump, if `flag` *false* then jump to label.

__flag *false*__
: Set `flag` to *false*.

__flag *true*__
: Set `flag` to *true*.

__match &lt;item&gt;__
: Compare one item with the input. Move input pointer forward.
If match the set `flag` *true*, else set `flag` to *false*.

__print &lt;item&gt;__
: Print current item to output.

__return__
: Return from call (pop from stack address and set the program counter).
Also pop positions of input and output pointers from a separate stack.

__stop__
: Stop the machine, print all of output.

__true &lt;label&gt;__
: Conditional jump, if `flag` is *true*.

This instruction set forms the backbone of a machine capable of parsing input strings
and generating structured output.


### Example

The machine can be applied to tasks such as parsing and converting infix expressions
into prefix notation. Consider the expression (45 + 89), which translates to the prefix
form + 45 89. Using abstraction, numeric values or variables can be represented by the
*placeholder* `i`.

Workflow

1. Assemble the source program etf.mc (short for expression, term, factor) into a binary
   format etf.b.

2. Run the binary program with an input file containing tokens like (,i,+,i,). This is
   internally parsed into a tokenized list: ['(', 'i', '+', 'i', ')'].

<!--
A sample 'etf.mc' (simple text) which is an abbreviation for
'expression, term, factor' is a program for converting infix
expressions to prefix expressions. One such expression could be
e.g. '(45+89)' which translates into '+ 45 89'. If we allow for
a simple abstraction, we can put 'i' as placeholder for numbers
or variables. This machine can thus be used for simple parsing.

First compile or assemble the program 'etf.mc' (source code) into
'etf.b' (binary). Then run the binary with a sample file 'etf.test'
such as `(,i,+,i,)`. This is then parsed into a list
`['(', 'i', '+', 'i', ')']` for easier handling of cases where
matching is done with concatenated characters into their own
tokens, e.g. 'ab'.-->
>
```shell
> python3 met.py -v -i etf.mc -o etf.b
> python3 calfe.py -v -t etf.test -i etf.b -o etf.out
```

The expected result for the input (,i,+,i,) is `+ i i`.

You can modify the test file etf.test to experiment with other expressions. For
instance, inputting `(,(,i,+,i,),*,i,+,(,i,*,i,*,i,),)` enables parsing more
complex structures.


[^metcalfe]: Howard H. Metcalfe, "A Parametrized Compiler based on Machanical Linguistics",
*Annual Review in Automatic Programming: International Tracts in Computer Science
and Technology and Their Application*, Vol. 4, ed. Richard Goodman, The Macmillan
Company, New York, 1964. Reprinted Pergamon Press, 2014.
Also see Mick Farmer, *Compiler physiology for beginners*, Chartwell-Bratt,
Bromley, 1985.
Another source which I find relevant is:
Hopcroft, John E., Motwani, Rajeev & Ullman, Jeffrey D., *Introduction to automata
theory, languages, and computation*, 3. ed., New international ed., Pearson
Addison-Wesley, Harlow, 2014.
