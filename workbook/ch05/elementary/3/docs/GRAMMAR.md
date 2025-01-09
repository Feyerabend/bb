
## Modified PL/0 Grammar in EBNF

The grammar of PL/0 can be expressed in Extended Backus-Naur Form (EBNF).
EBNF is a notation for formalising the grammar rules of a language.


```ebnf
<program>       ::= <block> "." .

<block>         ::= [ "const" <const-declaration> ";" ]
                    [ "var" <var-declaration> ";" ]
                    { "procedure" <ident> ";" <block> ";" }
                    <statement> .

<const-declaration> ::= <ident> "=" <number> { "," <ident> "=" <number> } .

<var-declaration>   ::= <ident> { "," <ident> } .

<statement>     ::= <assignment>
                 | <procedure-call>
                 | <begin-end>
                 | <if-statement>
                 | <while-statement>
                 | .

<assignment>    ::= <ident> ":=" <expression> .

<procedure-call>::= "call" <ident> .

<begin-end>     ::= "begin" <statement> { ";" <statement> { ";" } } "end" .

<if-statement>  ::= "if" <condition> "then" <statement> .

<while-statement> ::= "while" <condition> "do" <statement> .

<condition>     ::= "odd" <expression>
                 | <expression> <relational-operator> <expression> .

<relational-operator> ::= "=" | "#" | "<" | "<=" | ">" | ">=" .

<expression>    ::= [ "+" | "-" ] <term> { ("+" | "-") <term> } .

<term>          ::= <factor> { ("*" | "/") <factor> } .

<factor>        ::= <ident>
                 | <number>
                 | "(" <expression> ")" .

<ident>         ::= [a-zA-Z_][a-zA-Z_0-9]* .

<number>        ::= [0-9]+ .
```

Explanation of Grammar
1. Program Structure:
- A program consists of a block followed by a `.` to signify its end.

2. Block:
- A block may declare constants, variables, and procedures, followed by a main statement.

3. Declarations:
- const declarations assign constant values to identifiers.
- var declarations define variable names.
- procedure declarations define subprograms that can be invoked.

4. Statements:
- Statements are the building blocks of the program and include:
- Assignments (:=).
- Procedure calls (call).
- Compound statements enclosed in begin and end.
- Control flow like if and while.

5. Expressions:
- Expressions follow arithmetic rules, allowing operators (+, -, *, /) and parentheses.

6. Conditions:
- Conditions include both logical checks (odd) and relational operators (=, #, <, <=, >, >=).

7. Identifiers and Numbers:
- Identifiers are alphanumeric names starting with a letter or underscore.
- Numbers are sequences of digits.


### Example PL/0 Program

```pascal
const max = 100;

var arg, ret, answer;

procedure isprime;
var i;
begin
  ret := 1;
  i := 2;
  while (i < arg) do
    begin
      if (arg / i * i = arg) then
        begin
          ret := 0;
          i := arg
        end;
      i := i + 1
    end
end;

begin
  arg := 2;
  while (arg < max) do
    begin
      call isprime;
      if (ret = 1) then answer := arg;
      arg := arg + 1
    end
end.
```
