## Projects

The chapter on fundamentals in the book offers multiple avenues for exploration, each designed to
deepen your understanding of fundamental concepts.


### Example: Numbers

#### 1. Project: Integer representations in different bases

- Objective: Write a program to convert numbers between binary, octal, decimal, and hexadecimal.
  Implement the conversions ad understand the importance of each base and how they're used in
  computing (e.g., binary for logic, hexadecimal for compactness in memory addresses).

- Extension: Binary-Coded Decimal (BCD). Examine BCD, where each decimal digit is represented
  in binary. Explore why it's useful (e.g. decimal displays in calculators) and
  implement basic addition or subtraction with it to understand encoding limitations.

#### 2. Project: Creating a custom base or number representation

- Objective: Design your own base system (e.g. base-7 or base-12) and implement a converter
  that converts to and from this custom system to decimal. This exercise helps you to understand
  the flexibility of base systems and the algorithmic logic for base conversion.

- Extension: Non-positional systems. Implement simple arithmetic with Roman numerals, a
  non-positional system. This project can illustrate the practical limitations
  of such systems in complex computation, showing why positional systems are favored in
  computing.

#### 3. Project: Representing negative numbers in binary

- Objective: Implement positive and negative integers using two's complement and one's
  complement representations. Manually convert between decimal and two's complement binary
  and write a program that can perform addition and subtraction with it.

- Challenge: Explore edge cases, such as integer overflow and underflow, to understand
  the significance of bit-width limitations in two's complement arithmetic.

#### 4. Project: Investigating alternative numerical representations

- Objective: Experiment with unique representations like Gray code, where consecutive
  numbers differ by only one bit, and explore its applications (e.g., in error reduction
  for digital sensors).

- Challenge: Examine binary as a base for storing information in ways other than numbers,
  like characters (ASCII) or images (binary pixel representation). This will give you a
  broader understanding of how versatile binary is in computing beyond just encoding numbers.

#### 5. Project: Understanding checksum and parity in data transmission

- Objective: You can implement a simple parity check (single or double) to illustrate
  how error detection works in data transmission. Extend this by implementing a simple
  checksum algorithm to see how checksums verify data integrity in transmitted data.

- Challenge: Implement Hamming code for error correction, investigare how numerical
  representations directly impact data reliability in transmission.

#### 6. Project: Compare efficiency of different representations

- Objective: Compare efficiency and accuracy in different numerical systems by
  conducting a study. For instance, measure memory usage or computational speed for
  calculations in different formats (e.g., binary vs. BCD vs. floating-point) and
  analyze which is most efficient for specific types of calculations.

- Challenge: Research a use case (e.g., financial software, scientific computation,
  or graphics) and determine which number system or representation is best suited
  for it and why.


#### 7. Project: Simulating big numbers and arbitrary-precision arithmetic

- Objective: Implement basic operations (addition, subtraction, multiplication)
  for very large integers by storing digits in arrays. This introduces the concept
  of arbitrary precision, a foundation of BigInteger and BigDecimal classes that
  can be found in e.g. Java.

- Extension: Implement arbitrary-precision decimals to explore exact decimal
  arithmetic, avoiding floating-point imprecision and understanding where
  arbitrary-precision libraries are valuable in real applications.

#### 8. Project: Exploring floating-point arithmetic and precision limits

- Objective: Take floating-point representation (IEEE 754) and experiment with
  representing simple decimal values like 0.1, 0.2, etc., in floating-point format.
  Examine why operations like 0.1 + 0.2 might not equal 0.3 precisely.

- Extension: Create a simplified floating-point calculator that handles a limited
  range and precision. This illustrates how floating-point numbers approximate
  real numbers and the effect of rounding errors.


Here, as an *example* for exploring deeper, we focus on the representation of
numbers in computers, stemming from the mathematical constructs of
`real numbers.' We explore in code floating-point and fixed-point
representations, fractions, and symbolic calculations, as well as the strengths
and limitations of each approach. Code examples are provided to help you get
started with practical applications.

See more of this suggested [projects](./FLOATING.md) on floating-point to get started.


##### Float

A Python program that simulates floating-point arithmetic by decomposing numbers
into their sign, mantissa, and exponent components, in line with the
*IEEE 754 floating-point standard*.

* Code [float.py](./numbers/float.py).
* Description [FLOAT.md](./numbers/FLOAT.md).


##### Fixed

We start with something very small that represent a very small range of numbers,
as 2 bits are used for the integer part, and 3 bits for the fractional part.
It is in practice not very useful in general, but it easy to follow the calculations
and transformations of fixed point numbers in principal.

* Code [fixed23.c](./numbers/fixed32.c).
* Description [FIXED23.md](./numbers/FIXED23.md).

Next, we transfer to fixed point numbers that are useful such as Q16.16.

* Code [fixed.c](./numbers/fixed.c).
* Description [FIXED.md](./numbers/FIXED.md).


##### Fractions

Some programming languages offer built-in support for fractional numbers,
allowing developers to perform precise arithmetic using exact representations of
rational numbers. Python, for example, includes a Fraction type in its standard
library. This is particularly useful when floating-point arithmetic may introduce
rounding errors.

In contrast, C, as a low-level language, does not include native support for
fractions; any handling of fractions must be explicitly implemented or managed
by the programmer.

* Code [frac.c](./numbers/frac.c).
* Code [frac.py](./numbers/frac.py).

* Description [FRAC.md](./numbers/FRAC.md).

An extension of fractional numbers is the field of symbolic computation, which
allows to perform algebraic operations on expressions symbolically rather than
numerically. In symbolic computation, fractions remain in exact form and can be
manipulated as algebraic entities, and expressions can be expanded, factored,
or simplified without resort to approximation.

* Code [symb.c](./numbers/symb.c).
* Code [symb.py](./numbers/symb.py).

