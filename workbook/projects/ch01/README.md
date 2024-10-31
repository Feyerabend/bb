## Projects

This chapter in the book offers multiple avenues for exploration, each designed to
deepen your understanding of fundamental concepts.


### Numbers

Here, as an *example* for exploring, we focus on the representation of
real numbers in computers, stemming from the mathematical constructs of
`real numbers.' We explore in code floating-point and fixed-point
representations, fractions, and symbolic calculations, as well as the strengths
and limitations of each approach. Code examples are provided to help you get
started with practical applications.

You can further delve into how numbers are represented in various formats, such as
binary, octal, and hexadecimal, each of which plays a unique role in computing.
Additionally, explore more such as performing calculations with imaginary numbers
and understanding their applications. You can even examine unconventional
representations—like calculating with Roman numerals—to illustrate the diversity
of numerical systems and the implications for computation.

See more of the suggested [projects](./FLOATING.md) on floating-point.
Some initial help has been added:


### Float

A Python program that simulates floating-point arithmetic by decomposing numbers
into their sign, mantissa, and exponent components, in line with the
*IEEE 754 floating-point standard*.

* Code [float.py](./numbers/float.py)
* Description [FLOAT.md](./numbers/FLOAT.md)


### Fixed

We start with something very small that represent a very small range of numbers,
as 2 bits are used for the integer part, and 3 bits for the fractional part.
It is in practice not very useful in general, but it easy to follow the calculations
and transformations of fixed point numbers in principal.

* Code [fixed23.c](./numbers/fixed32.c)
* Description [FIXED23.md](./numbers/FIXED23.md)

Next, we transfer to fixed point numbers that are useful such as Q16.16.

* Code [fixed.c](./numbers/fixed.c)
* Description [FIXED.md](./numbers/FIXED.md)


### Fractions

Some programming languages offer built-in support for fractional numbers,
allowing developers to perform precise arithmetic using exact representations of
rational numbers. Python, for example, includes a Fraction type in its standard
library. This is particularly useful when floating-point arithmetic may introduce
rounding errors.

In contrast, C, as a low-level language, does not include native support for
fractions; any handling of fractions must be explicitly implemented or managed
by the programmer.

* Code [frac.c](./numbers/frac.c)
* Code [frac.py](./numbers/frac.py)

* Description [FRAC.md](./numbers/FRAC.md)

An extension of fractional numbers is the field of symbolic computation, which
allows to perform algebraic operations on expressions symbolically rather than
numerically. In symbolic computation, fractions remain in exact form and can be
manipulated as algebraic entities, and expressions can be expanded, factored,
or simplified without resort to approximation.

* Code [symb.c](./numbers/symb.c)
* Code [symb.py](./numbers/symb.py)

