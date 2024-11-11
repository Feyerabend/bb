
## ENBF

```enbf
Program      ::= { Command | Number | Literal | Array | Block }*

Command      ::= "push" | "pop" | "dup" | "swap" | "over"
               | "add" | "sub" | "mul" | "div"
               | "if" | "for" | "exit"
               | "gsave" | "grestore"
               | "moveto" | "lineto" | "stroke" | "fill"
               | "newpath" | "closepath"
               | "setlinewidth" | "setcolor"
               | "array" | "get" | "put"

Number       ::= [ "-" ] Digit { Digit } [ "." Digit { Digit } ]
Literal      ::= "/" Name
Name         ::= Letter { Letter | Digit | "_" }
Array        ::= "[" { Number | Literal | Command } "]"
Block        ::= "{" { Command | Number | Literal | Array } "}"

Letter       ::= "a" | "b" | ... | "z" | "A" | "B" | ... | "Z"
Digit        ::= "0" | "1" | ... | "9"
```