
## Pushdown Automaton

A PDA can recognize context-free languages. Here's a simple PDA to recognize
the language 
$$\[
    L = \\{ a^n b^n \mid n \geq 0 \\}
\]$$
(equal numbers of 'a' followed by 'b').
The stack grows with each a and shrinks with each b.

```python
class PushdownAutomaton:
    def __init__(self):
        self.stack = []
        self.state = "q0"  # start state

    def transition(self, state, symbol):
        if state == "q0":
            if symbol == 'a':
                self.stack.append('A')
                return "q0"  # stay in q0 while reading a's
            elif symbol == 'b' and self.stack:
                self.stack.pop()
                return "q1"  # transition to q1 when reading the first b
        elif state == "q1":
            if symbol == 'b' and self.stack:
                self.stack.pop()
                return "q1"  # stay in q1 while reading b's
        return None  # invalid state or transition

    def accepts(self, input_string):
        self.stack = []
        self.state = "q0"

        for symbol in input_string:
            self.state = self.transition(self.state, symbol)
            if self.state is None:
                return False  # invalid transition or stack mismatch

        # accept if in final state and stack is empty
        return self.state == "q1" and not self.stack


# test
pda = PushdownAutomaton()
print(pda.accepts("aabb"))    # True, valid balanced string
print(pda.accepts("aaabbb"))  # True, valid balanced string
print(pda.accepts("abab"))    # False, invalid order
print(pda.accepts("aab"))     # False, unbalanced string
print(pda.accepts("baab"))    # False, invalid order
```


### What is a Pushdown Automaton (PDA)?

A Pushdown Automaton (PDA) is a computational model used to recognize
context-free languages (CFLs). It is an extension of a finite automaton
(FA) that includes a stack as an auxiliary memory. The stack enables the
PDA to handle nested or recursive structures, which finite automata alone
cannot process.


### Components of a PDA

A PDA has:
1. States: A finite set of states (like in finite automata).
2. Input Alphabet: Symbols that the PDA reads from the input string.
3. Stack Alphabet: Symbols that can be pushed to or popped from the stack.
4. Stack: A memory structure where elements are added (pushed) and removed
   (popped) following the last in, first out (LIFO) principle.
5. Transition Function: Defines how the PDA moves between states, based on:
    - The current state.
    - The current input symbol (or epsilon for no input).
    - The top symbol on the stack.
6. Start State: The state where the computation begins.
7. Accepting States: A set of states that signify successful parsing.


### How Does a PDA Work?

a. The PDA reads an input string one symbol at a time.

b. For each symbol:

    1. It checks the current state.

    2. It checks the symbol on top of the stack.

    3. It decides:

	    - Whether to push, pop, or leave the stack unchanged.

	    - Which state to transition to next.

	    - At the end, the input is accepted if:

    	    - The PDA is in an accepting state and/or

	        - The stack is empty (depending on the PDA's design).


### Where is a PDA Used?

PDAs are primarily used in:
* Compilers and Parsers: Parsing programming languages with context-free grammars (CFGs), such as arithmetic expressions.
* Parentheses Matching: Ensuring properly nested brackets, such as in ${[()()]}$.
* Natural Language Processing: Handling grammars with recursion or hierarchy.
* XML Parsing: Ensuring matching and nesting of tags.
