## Projects

This chapter in the book offers multiple avenues for exploration, each designed to
deepen your understanding of fundamental concepts. Here, as an example for exploring,
we focus on the representation of real numbers in computers, stemming from the mathematical
constructs of `real numbers.' We explore in code floating-point and fixed-point
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

Below are some general aspects on the number representations as an overview,
from which you can draw your own projects.


### Fixed-Point numbers

*   Fixed-point numbers represent real numbers as integers scaled by a fixed factor,
    typically a power of two or ten. This approach offers a balance between performance
    and precision, making it suitable for applications with predictable ranges and
    precision needs, such as embedded systems.

*   A fixed-point library in C can handle arithmetic operations like addition,
    subtraction, multiplication, division, and modulo, as well as conversions between
    fixed-point and floating-point representations.

*   The Qm.n format is a common way to denote fixed-point representations, with 'm'
    bits for the integer part and 'n' bits for the fractional part. For example,
    Q2.3 allocates 2 bits for the integer and 3 bits for the fractional part,
    allowing representation of numbers ranging from -2 to 1 in the integer part
    and 0 to 0.875 in the fractional part.

*   Arithmetic operations on fixed-point numbers involve integer arithmetic with
    appropriate scaling and shifting to maintain precision. For example, multiplication
    requires shifting the result right by the number of fractional bits to account
    for the fixed-point scaling.

*   Fixed-point numbers have limitations in representing very large or very small
    numbers and can suffer from overflow issues. They also offer limited precision
    compared to floating-point numbers, leading to potential rounding errors.

### Floating-Point numbers

*   Floating-point numbers provide a wider dynamic range and higher precision compared
    to fixed-point numbers. They are represented using the IEEE 754 standard, which
    defines single, double, and extended precision formats.

*   A floating-point number consists of three parts: the sign bit, exponent, and mantissa.
    *   The sign bit indicates whether the number is positive or negative.
    *   The exponent determines the range of values, enabling representation of very large
        or very small numbers.
    *   The mantissa contains the actual digits of the number, affecting the precision.

*   Python code can be used to emulate floating-point arithmetic by breaking down numbers
    into their sign, mantissa, and exponent components according to the IEEE 754 standard.
    This involves converting decimal values into a binary floating-point representation,
    performing operations, and displaying the results.

*   Floating-point numbers can encounter challenges such as rounding errors, overflow,
    and underflow. They also struggle to represent certain numbers exactly due to the
    limitations of binary representation.

### Comparison and alternatives

*   Floating-point numbers are generally preferred for applications where approximate
    values are acceptable and speed is essential, such as real-time graphics. However,
    they are prone to precision loss, especially in iterative processes or calculations
    involving both large and small numbers.

*   Several alternatives to floating-point representation exist, each with its own
    strengths and weaknesses:

    *   *Fixed-Point Representation*: Suitable for applications with predictable range
        and precision needs, like embedded systems. Fixed-point numbers avoid some rounding
        issues but have limited dynamic range.

    *   *Arbitrary-Precision Arithmetic*: Provides more precise calculations by allocating
        more bits for storage as needed. This approach is slower than fixed-precision but
        is valuable in fields like cryptography or symbolic computation where exact results
        are crucial.

    *   *Rational Numbers*: Represented as fractions, rational numbers can avoid precision
        loss in certain calculations and are sometimes used in algebraic computation systems.

    *   *Interval Arithmetic*: Uses ranges to bound calculations, managing precision in
        critical applications such as physics simulations.

### Fractional numbers and symbolic logic

*   Fractions can be represented using both floating-point and rational numbers. Rational
    numbers offer higher precision in mathematical calculations by directly working with
    numerators and denominators instead of decimal approximations.

*   Implementing fractional arithmetic involves applying specific rules for addition,
    subtraction, multiplication, and division, and simplifying the resulting fractions by
    finding the greatest common divisor (GCD).

*   Symbolic logic can enhance the flexibility and expressiveness of fractional number
    calculations. This involves representing operations and expressions symbolically,
    potentially with lazy evaluation, and enabling conditional logic based on the properties
    of the fractions.

*   Python and C examples demonstrate the implementation of fraction classes and symbolic
    fraction classes that support arithmetic operations, comparisons, and conditional
    expressions.

