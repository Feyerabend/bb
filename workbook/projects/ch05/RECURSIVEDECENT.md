Creating recursive descent parsers for simplified versions of LISP, BASIC, and PASCAL in C and Python can be an interesting exercise. Below are implementations for each of these languages. Each parser will handle a small set of syntactic constructs.

### 1. Simplified LISP Parser

**Grammar:**
```
S → ( A )
A → a A | ε
```

#### C Implementation

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *input;
int pos = 0;

char lookahead() {
    return input[pos];
}

void eat(char expected) {
    if (lookahead() == expected) {
        pos++;
    } else {
        printf("Error: Expected '%c' but found '%c'\n", expected, lookahead());
        exit(1);
    }
}

void A() {
    while (lookahead() == 'a') {
        eat('a');
    }
}

void S() {
    eat('(');
    A();
    eat(')');
}

int main() {
    input = "(aa)";  // Example input
    S();
    if (lookahead() == '\0') {
        printf("LISP input parsed successfully!\n");
    } else {
        printf("Error: Unexpected input at end\n");
    }
    return 0;
}
```

#### Python Implementation

```python
class LispParser:
    def __init__(self, input):
        self.input = input
        self.pos = 0

    def lookahead(self):
        return self.input[self.pos] if self.pos < len(self.input) else None

    def eat(self, expected):
        if self.lookahead() == expected:
            self.pos += 1
        else:
            raise Exception(f"Error: Expected '{expected}' but found '{self.lookahead()}'")

    def A(self):
        while self.lookahead() == 'a':
            self.eat('a')

    def S(self):
        self.eat('(')
        self.A()
        self.eat(')')

    def parse(self):
        self.S()
        if self.lookahead() is None:
            print("LISP input parsed successfully!")
        else:
            print("Error: Unexpected input at end")

# Example usage
input_string = "(aa)"
parser = LispParser(input_string)
parser.parse()
```

---

### 2. Simplified BASIC Parser

**Grammar:**
```
S → PRINT E
E → NUMBER | STRING
NUMBER → [0-9]+
STRING → "[a-zA-Z]*"
```

#### C Implementation

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

char *input;
int pos = 0;

char lookahead() {
    return input[pos];
}

void eat(char expected) {
    if (lookahead() == expected) {
        pos++;
    } else {
        printf("Error: Expected '%c' but found '%c'\n", expected, lookahead());
        exit(1);
    }
}

void E() {
    if (isdigit(lookahead())) {
        while (isdigit(lookahead())) eat(lookahead());
    } else if (lookahead() == '"') {
        eat('"');
        while (isalpha(lookahead())) eat(lookahead());
        eat('"');
    } else {
        printf("Error: Expected NUMBER or STRING\n");
        exit(1);
    }
}

void S() {
    eat('P');
    eat('R');
    eat('I');
    eat('N');
    eat('T');
    E();
}

int main() {
    input = "PRINT 123";  // Example input
    S();
    if (lookahead() == '\0') {
        printf("BASIC input parsed successfully!\n");
    } else {
        printf("Error: Unexpected input at end\n");
    }
    return 0;
}
```

#### Python Implementation

```python
class BasicParser:
    def __init__(self, input):
        self.input = input
        self.pos = 0

    def lookahead(self):
        return self.input[self.pos] if self.pos < len(self.input) else None

    def eat(self, expected):
        if self.lookahead() == expected:
            self.pos += 1
        else:
            raise Exception(f"Error: Expected '{expected}' but found '{self.lookahead()}'")

    def E(self):
        if self.lookahead().isdigit():
            while self.lookahead().isdigit():
                self.eat(self.lookahead())
        elif self.lookahead() == '"':
            self.eat('"')
            while self.lookahead() and self.lookahead().isalpha():
                self.eat(self.lookahead())
            self.eat('"')
        else:
            raise Exception("Error: Expected NUMBER or STRING")

    def S(self):
        for char in "PRINT":
            self.eat(char)
        self.E()

    def parse(self):
        self.S()
        if self.lookahead() is None:
            print("BASIC input parsed successfully!")
        else:
            print("Error: Unexpected input at end")

# Example usage
input_string = 'PRINT "Hello"'
parser = BasicParser(input_string)
parser.parse()
```

---

### 3. Simplified PASCAL Parser

**Grammar:**
```
S → BEGIN E END
E → ID := NUMBER
ID → [a-zA-Z][a-zA-Z0-9]*
NUMBER → [0-9]+
```

#### C Implementation

```c
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

char *input;
int pos = 0;

char lookahead() {
    return input[pos];
}

void eat(char expected) {
    if (lookahead() == expected) {
        pos++;
    } else {
        printf("Error: Expected '%c' but found '%c'\n", expected, lookahead());
        exit(1);
    }
}

void ID() {
    if (isalpha(lookahead())) {
        eat(lookahead());
        while (isalnum(lookahead())) eat(lookahead());
    } else {
        printf("Error: Expected ID\n");
        exit(1);
    }
}

void E() {
    ID();
    eat('=');
    while (isdigit(lookahead())) eat(lookahead());
}

void S() {
    eat('B');
    eat('E');
    eat('G');
    eat('I');
    eat('N');
    E();
    eat('E');
    eat('N');
    eat('D');
}

int main() {
    input = "BEGIN x := 123 END";  // Example input
    S();
    if (lookahead() == '\0') {
        printf("PASCAL input parsed successfully!\n");
    } else {
        printf("Error: Unexpected input at end\n");
    }
    return 0;
}
```

#### Python Implementation

```python
class PascalParser:
    def __init__(self, input):
        self.input = input
        self.pos = 0

    def lookahead(self):
        return self.input[self.pos] if self.pos < len(self.input) else None

    def eat(self, expected):
        if self.lookahead() == expected:
            self.pos += 1
        else:
            raise Exception(f"Error: Expected '{expected}' but found '{self.lookahead()}'")

    def ID(self):
        if self.lookahead().isalpha():
            self.eat(self.lookahead())
            while self.lookahead() and self.lookahead().isalnum():
                self.eat(self.lookahead())
        else:
            raise Exception("Error: Expected ID")

    def E(self):
        self.ID()
        self.eat('=')
        while self.lookahead().isdigit():
            self.eat(self.lookahead())

    def S(self):
        for char in "BEGIN":
            self.eat(char)
        self.E()
        for char in "END":
            self.eat(char)

    def parse(self):
        self.S()
        if self.lookahead() is None:
            print("PASCAL input parsed successfully!")
        else:
            print("Error: Unexpected input at end")

# Example usage
input_string = "BEGIN x := 123 END"
parser = PascalParser(input_string)
parser.parse()
```

### Summary

Each parser follows the grammar rules defined and provides basic handling of specific constructs for each simplified language. You can test and modify these parsers by changing the input strings according to the grammar rules. Adjustments may be necessary to extend the grammar or handle additional constructs as needed.
