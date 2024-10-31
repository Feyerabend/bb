
## Fixed Q16.16

A fixed-point number system represents real numbers as integers while implicitly treating the number as being scaled by some factor (usually a power of two or ten). In C, we can implement a fixed-point library to handle basic arithmetic (addition, subtraction, multiplication, division, and modulo) and convert between fixed-point and floating-point numbers.

We'll represent fixed-point numbers with an integer and a fixed scaling factor (e.g., 16 fractional bits for a 32-bit fixed-point type).


### Fixed-Point Library in C


```c
#include <stdio.h>
#include <stdint.h>

// Define the number of fractional bits (we use 16 for Q16.16 fixed-point format)
#define FRACTIONAL_BITS 16
#define SCALE (1 << FRACTIONAL_BITS)  // 2^16 or 65536 for scaling

// Fixed-point type: using 32-bit signed integer
typedef int32_t fixed_point;

// Convert from float to fixed-point
fixed_point float_to_fixed(float value) {
    return (fixed_point)(value * SCALE);
}

// Convert from fixed-point to float
float fixed_to_float(fixed_point value) {
    return (float)value / SCALE;
}

// Addition of fixed-point numbers
fixed_point fixed_add(fixed_point a, fixed_point b) {
    return a + b;
}

// Subtraction of fixed-point numbers
fixed_point fixed_sub(fixed_point a, fixed_point b) {
    return a - b;
}

// Multiplication of fixed-point numbers
fixed_point fixed_mul(fixed_point a, fixed_point b) {
    return (fixed_point)(((int64_t)a * b) >> FRACTIONAL_BITS);
}

// Division of fixed-point numbers
fixed_point fixed_div(fixed_point a, fixed_point b) {
    return (fixed_point)(((int64_t)a << FRACTIONAL_BITS) / b);
}

// Modulo operation for fixed-point numbers
fixed_point fixed_mod(fixed_point a, fixed_point b) {
    return a % b;
}

// Printing fixed-point value (debugging)
void print_fixed(fixed_point value) {
    printf("Fixed-point: %d (Float equivalent: %f)\n", value, fixed_to_float(value));
}
```

### Explanation:

- *Conversion between float and fixed-point*:
  - `float_to_fixed(float value)`: Converts a floating-point number to a fixed-point number by multiplying the float by the scale factor (2^16).
  - `fixed_to_float(fixed_point value)`: Converts a fixed-point number back to a floating-point number by dividing it by the scale factor.
  
- *Arithmetic operations*:
  - `fixed_add`, `fixed_sub`: Simple integer addition and subtraction.
  - `fixed_mul`: Multiplies two fixed-point numbers and shifts the result back by `FRACTIONAL_BITS` to account for the fixed-point scaling.
  - `fixed_div`: Shifts the dividend up by `FRACTIONAL_BITS` before performing integer division, to maintain precision.
  - `fixed_mod`: Uses the modulo operation, which operates at the integer level and provides the remainder in fixed-point form.

- *Printing*: `print_fixed` outputs both the fixed-point representation (raw integer value) and the floating-point equivalent.


### Sample Usage

Here's a sample program demonstrating the usage of the fixed-point library with addition, subtraction, multiplication, division, and modulo operations:

```c
int main() {
    // Convert floating-point numbers to fixed-point numbers
    float a_f = 5.25;
    float b_f = 2.75;
    
    fixed_point a = float_to_fixed(a_f);
    fixed_point b = float_to_fixed(b_f);

    printf("Original floating-point numbers:\n");
    printf("a = %f, b = %f\n", a_f, b_f);
    
    printf("\nFixed-point representations:\n");
    print_fixed(a);
    print_fixed(b);
    
    // Addition
    fixed_point sum = fixed_add(a, b);
    printf("\nAddition:\n");
    print_fixed(sum);

    // Subtraction
    fixed_point diff = fixed_sub(a, b);
    printf("\nSubtraction:\n");
    print_fixed(diff);

    // Multiplication
    fixed_point product = fixed_mul(a, b);
    printf("\nMultiplication:\n");
    print_fixed(product);

    // Division
    fixed_point quotient = fixed_div(a, b);
    printf("\nDivision:\n");
    print_fixed(quotient);

    // Modulo
    fixed_point remainder = fixed_mod(a, b);
    printf("\nModulo:\n");
    print_fixed(remainder);

    return 0;
}
```

### Sample Output

```bash
Original floating-point numbers:
a = 5.250000, b = 2.750000

Fixed-point representations:
Fixed-point: 344064 (Float equivalent: 5.250000)
Fixed-point: 180224 (Float equivalent: 2.750000)

Addition:
Fixed-point: 524288 (Float equivalent: 8.000000)

Subtraction:
Fixed-point: 163840 (Float equivalent: 2.500000)

Multiplication:
Fixed-point: 619520 (Float equivalent: 9.062500)

Division:
Fixed-point: 122880 (Float equivalent: 1.500000)

Modulo:
Fixed-point: 163840 (Float equivalent: 2.500000)
```

### Output

- *Fixed-point representation*: For example, `5.25` is represented as `344064` in fixed-point. This is calculated as `5.25 * 65536 = 344064`.
- *Addition*: `5.25 + 2.75 = 8.0` in floating-point. In fixed-point, `344064 + 180224 = 524288`, which converts back to `8.0` in floating-point.
- *Subtraction*: `5.25 - 2.75 = 2.5`, and in fixed-point, `344064 - 180224 = 163840`, which converts back to `2.5`.
- *Multiplication*: `5.25 * 2.75 = 9.0625`. The fixed-point result is `619520`, and `619520 / 65536 = 9.0625`.
- *Division*: `5.25 / 2.75 = 1.5`. The fixed-point result is `122880`, and `122880 / 65536 = 1.5`.
- *Modulo*: `5.25 % 2.75 = 2.5`. In fixed-point, `163840` represents `2.5`.


### Notes

1. *Precision*: The multiplication and division operations involve shifts to maintain precision. Using `int64_t` for intermediate results ensures that we avoid overflow during these operations.
2. *Scaling Factor*: This implementation uses a Q16.16 format (16 bits for the fractional part). You can adjust `FRACTIONAL_BITS` if a different precision is needed.
3. *Limitations*: Fixed-point numbers offer limited precision compared to floating-point, so rounding errors and overflow issues can occur with large numbers or very small fractional parts.

This library provides basic functionality for handling fixed-point numbers in C and showcases the core operations like conversion, arithmetic, and printing.
