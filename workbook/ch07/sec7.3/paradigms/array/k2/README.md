# K Interpreter - Improved Version

## Overview

This is an improved implementation of a K-like array programming language interpreter. K is a powerful array programming language known for its concise syntax and efficient operations on vectors and matrices.

## Key Improvements Over Original

### 1. **Better Error Handling**
- **Custom exception class (`KError`)** with error type categorization
- **Enum for error types** (SYNTAX, TYPE, RANK, DOMAIN, INDEX, LENGTH, UNDEFINED)
- More informative error messages that specify the type of error
- Consistent error handling across all operations

### 2. **Enhanced Documentation**
- **Comprehensive docstrings** for all functions explaining what they do
- **Type hints** throughout the code for better IDE support
- **Clear section organization** with comment headers
- **README** explaining usage and features

### 3. **Improved Code Structure**
- **Separated concerns**: type checking, operations, parsing, REPL
- **More consistent naming** conventions
- **Better function organization** with logical grouping
- **Cleaner operation registry** with description field used consistently

### 4. **Additional Features**
- **Help command** in REPL shows all available operations
- **Vars command** displays current variables
- **List operations** utility method for seeing what's available
- **File execution** mode to run K scripts from files
- **Better REPL** with clearer prompts and output

### 5. **Code Quality**
- **Reduced code duplication** through helper functions
- **More defensive programming** with better edge case handling
- **Improved readability** with shorter, more focused functions
- **Better separation** of parsing and evaluation logic

### 6. **Bug Fixes**
- Fixed potential issues with nested list/dict parsing
- Better handling of empty lists and dictionaries
- Improved string parsing for edge cases
- More robust variable lookup

## Installation

No external dependencies required - uses only Python standard library.

```bash
# Make the script executable
chmod +x k_interpreter.py

# Run the REPL
python3 k_interpreter.py

# Or run a K script file
python3 k_interpreter.py script.k
```

## Usage

### Interactive REPL

```bash
$ python3 k_interpreter.py
K Interpreter
Type 'exit' to quit, 'help' for operations list, 'vars' to see variables

  !5
[0, 1, 2, 3, 4]
  x:10
10
  x+5
15
  help
Available operations:
    ! (  monadic, dyadic) - Generate sequence (monadic) or modulo (dyadic)
    # (  monadic, dyadic) - Length of list (monadic) or take elements (dyadic)
  ...
```

### Running Examples

```bash
# Run the comprehensive example suite
python3 k_examples.py
```

### Commands in REPL

- **`exit`** - Exit the interpreter
- **`help`** - List all available operations with descriptions
- **`vars`** - Show all defined variables
- **`name:expression`** - Assign result to variable

## Quick Reference

### Basic Operations

| Symbol | Monadic | Dyadic | Example |
|--------|---------|--------|---------|
| `+` | Sum | Add | `+/1 2 3` → 6, `1+2` → 3 |
| `-` | Negate | Subtract | `-5` → -5, `10-3` → 7 |
| `*` | Maximum | Multiply | `*1 2 3` → 3, `2*3` → 6 |
| `%` | Average | Divide | `%10 20 30` → 20.0, `50%100` → 50.0 |
| `!` | Iota | Modulo | `!5` → 0 1 2 3 4, `3!10` → 1 |
| `#` | Length | Take | `#"hello"` → 5, `3#1 2 3 4` → 1 2 3 |
| `_` | - | Drop | `2_1 2 3 4` → 3 4 |
| `?` | Unique | Find | `?1 2 2 3` → 1 2 3, `2?1 2 2 3` → 1 2 |
| `,` | Enlist | Join | `,5` → [5], `1 2,3 4` → 1 2 3 4 |
| `@` | First | Index | `@1 2 3` → 1, `1 2 3@1` → 2 |
| `^` | Where | Group | `^1 0 2` → 0 2 2, - |
| `&` | Minimum | AND | `&1 2 3` → 1, `5&3` → 1 |
| `\|` | Reverse | OR | `\|1 2 3` → 3 2 1, `5\|3` → 7 |
| `=` | - | Equal | `1 2 3=2` → 0 1 0 |
| `~` | - | Not equal | `1 2 3~2` → 1 0 1 |
| `` ` `` | Sort | - | `` `3 1 2`` → 1 2 3 |
| `;` | Raze/Flatten | - | `;(1 2;3 4)` → 1 2 3 4 |
| `.` | Transpose | - | `.(1 2;3 4)` → (1 3;2 4) |
| `:` | Coalesce | - | `:null null 5` → 5 |
| `$` | Type | Dict lookup | `$5` → "i" |

### Data Types

```k
42          # integer
3.14        # float
"hello"     # string
true false  # boolean
(1;2;3)     # list
[a:1;b:2]   # dictionary
```

### Variables

```k
x:10           # assign
y:x+5          # use variable
nums:(1;2;3)   # list variable
```

### Examples

```k
# Generate first 10 numbers
!10
# → [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Sum them
+!10
# → 45

# Vector addition
(1;2;3)+(10;20;30)
# → [11, 22, 33]

# Filter even numbers
nums:!10
evens:(^(2!nums)=0)
nums@evens
# → [0, 2, 4, 6, 8]

# Matrix transpose
matrix:((1;2;3);(4;5;6))
.matrix
# → [[1, 4], [2, 5], [3, 6]]

# String operations
|"hello"
# → "olleh"

# Dictionary
d:["name":"Alice";"age":30]
d$"name"
# → "Alice"
```

## Error Types

The interpreter provides helpful error messages categorized by type:

- **syntax error** - Invalid expression syntax
- **type error** - Operation on incompatible types
- **rank error** - Operation on wrong rank (scalar vs vector)
- **domain error** - Invalid domain for operation
- **index error** - Out of bounds access
- **length error** - Mismatched lengths in operations
- **undefined variable** - Reference to undefined variable

## Differences from Real K

This is a simplified educational interpreter. Notable differences:

1. **Limited adverbs** - No `/` (fold), `\` (scan), `'` (each) yet
2. **Simpler parsing** - No complex projection or composition
3. **Basic types** - No symbols, dates, or specialized types
4. **Python integration** - Uses Python types under the hood

## Architecture

```
k_interpreter.py
├── Type System (is_atomic, get_type)
├── Monadic Operations (negate, sum, reverse, etc.)
├── Dyadic Operations (add, multiply, index, etc.)
├── Operation Registry (register, lookup)
├── Parser (parse_value, evaluate_expression)
└── REPL (interactive loop)
```

## Testing

Run the comprehensive test suite:

```bash
python3 k_examples.py
```

This runs ~50 examples covering:
- Arithmetic operations
- Vector operations
- List manipulation
- String operations
- Matrix operations
- Dictionary operations
- Type system
- And more...

## Contributing

Areas for potential enhancement:
1. Add adverbs (fold `/`, scan `\`, each `'`)
2. Implement projection and function composition
3. Add more K operations (like grade, where-each, etc.)
4. Performance optimization for large arrays
5. Better pretty-printing of results
6. Save/load workspace functionality

## License

Educational/demonstration code - use freely.

## References

- [K Language](https://en.wikipedia.org/wiki/K_(programming_language))
- [Shakti K Tutorial](https://shakti.com/)
- [ngn/k](https://codeberg.org/ngn/k)
