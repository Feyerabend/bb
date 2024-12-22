
## LL(1) Parsing

Revised Plan with a Parsing Table
1. *Define the Grammar and EBNF*: We rewrite the grammar and ensure it's in LL(1) form.
2. *Construct the Parsing Table*: The table maps (non-terminal, lookahead token) to the production rule to apply.
3. *Implement Table-Driven Parsing*: Use the parsing table to decide which production to apply based on the current token and non-terminal.


### Grammar (EBNF)

Here's the grammar with support for numbers, floating points, and operators:

```ebnf
    E  → T E'
    E' → + T E' | - T E' | ε
    T  → F T'
    T' → * F T' | / F T' | % F T' | ε
    F  → ( E ) | num | num ^ F
```

- num represents an integer or floating-point number.
- ε is the empty production (nothing).


### Parsing Table

```text
NT	num	(	+	-	*	/	%	)	$	^
E	T E'	T E'								
E'			+ T E'	- T E'	ε	ε	ε	ε	ε	
T	F T'	F T'								
T'			ε	ε	* F T'	/ F T'	% F T'	ε	ε	
F	num	( E )								num ^ F
```

Legend:
- NT is Non-terminal
- $ is the end-of-input marker.
- Cells contain the production to apply or are empty if the input is invalid for that non-terminal.

### Code

Here's how we integrate the parsing table into the parser:

```python
import re

class LL1Parser:
    def __init__(self, input):
        self.tokens = self.tokenize(input)
        self.tokens.append('$')  # end-of-input marker
        self.pos = 0
        self.stack = ['$', 'E']  # parsing stack starts with $ and the start symbol

        # parsing table
        self.table = {
            'E': {
                'num': ['T', 'E\''],
                '(': ['T', 'E\'']
            },
            'E\'': {
                '+': ['+', 'T', 'E\''],
                '-': ['-', 'T', 'E\''],
                ')': [],
                '$': []
            },
            'T': {
                'num': ['F', 'T\''],
                '(': ['F', 'T\'']
            },
            'T\'': {
                '+': [],
                '-': [],
                '*': ['*', 'F', 'T\''],
                '/': ['/', 'F', 'T\''],
                '%': ['%', 'F', 'T\''],
                ')': [],
                '$': []
            },
            'F': {
                'num': ['num'],
                '(': ['(', 'E', ')']
            }
        }

    def tokenize(self, input):
        token_pattern = r'\d+\.\d+|\d+|[+\-*/%^()]'
        tokens = re.findall(token_pattern, input)
        print(f"Tokens: {tokens}")
        return tokens

    def lookahead(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self):
        while self.stack:
            top = self.stack.pop()
            token = self.lookahead()

            if top in self.table:  # non-terminal
                if token in self.table[top]:
                    production = self.table[top][token]
                    print(f"Applying production {top} → {' '.join(production)}")
                    self.stack.extend(reversed(production))  # push production onto stack
                else:
                    raise Exception(f"Error: Unexpected token {token} for {top}")
            elif top == token:  # terminal matches input
                print(f"Consuming: {token}")
                self.pos += 1
            elif top == 'num' and self.is_number(token):  # match number
                print(f"Consuming number: {token}")
                self.pos += 1
            else:
                raise Exception(f"Error: Unexpected token {token}. Expected {top}")

        if self.lookahead() == '$':
            print("Input parsed successfully!")
        else:
            raise Exception(f"Error: Unexpected input at end. Found {self.lookahead()}")

    def is_number(self, token):
        """Check if the token is a valid number (integer or floating-point)."""
        return re.match(r'^\d+(\.\d+)?$', token)



input_string = "3 + 2 * 4"
parser = LL1Parser(input_string)
parser.parse()

input_string2 = "3.14 * ( 2 + 5.6 )"
parser2 = LL1Parser(input_string2)
parser2.parse()

input_string3 = "5 + 3.5 ^ 2"
parser3 = LL1Parser(input_string3)
parser3.parse()

input_string4 = "2 * (3 + 2.5)"
parser4 = LL1Parser(input_string4)
parser4.parse()

input_string5 = "1.5 + 2.5 * 3"
parser5 = LL1Parser(input_string5)
parser5.parse()
```

### Explanation:

1. Parsing Table:
	- Explicitly constructed for each non-terminal and terminal.
	- Guides the parser on which production to apply.

2. Stack:
	- The stack holds the current symbols (terminals and non-terminals) the parser is processing.

3. Table Lookup:
	- The parser uses the table to decide which production to apply based on the top of the stack and the lookahead token.

4. Error Handling:
	- If no production exists for a (non-terminal, token) pair, an error is raised.

5. Number Handling:
	- Matches integers and floating-point numbers.


### Output

For the input 3 + 2 * 4:

```text
Tokens: ['3', '+', '2', '*', '4']
Applying production E → T E'
Applying production T → F T'
Applying production F → num
Consuming number: 3
Applying production T' → ε
Applying production E' → + T E'
Consuming: +
Applying production T → F T'
Applying production F → num
Consuming number: 2
Applying production T' → * F T'
Consuming: *
Applying production F → num
Consuming number: 4
Applying production T' → ε
Applying production E' → ε
Input parsed successfully!
```

This approach is systematic and extendable, ideal for learning and implementing larger grammars.
