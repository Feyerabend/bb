## Fixed Q2.3

### Representation of 2.3

When we use *2.3* as our model for fixed-point representation, we will choose a fixed-point format,
say *Qm.n*, where `m` is the integer part, and `n` is the fractional part.

#### Example

In the *Q2.3* format:
- *2 bits* are allocated for the integer part.
- *3 bits* are allocated for the fractional part.

This means the maximum value we can represent is:
- *Integer Range*: From -2 to 1 (in binary: `10` to `01`).
- *Fractional Range*: Represented as `0.0` to `0.875` (as 0.111 in binary is $`\frac{7}{8}`$).

### Conversion of 2.3 to Fixed-Point

To represent *2.3* in this format:
1. *Integer Part*: The integer part of 2.3 is `2`, which is represented as `10` in binary.
2. *Fractional Part*: The fractional part `.3` needs to be converted to binary.
   - To find the binary representation of `.3`, we can multiply by 2 iteratively:
     - \( 0.3 \times 2 = 0.6 \)  → 0 (whole part), carry forward 0.6
     - \( 0.6 \times 2 = 1.2 \)  → 1 (whole part), carry forward 0.2
     - \( 0.2 \times 2 = 0.4 \)  → 0 (whole part), carry forward 0.4
     - \( 0.4 \times 2 = 0.8 \)  → 0 (whole part), carry forward 0.8
     - \( 0.8 \times 2 = 1.6 \)  → 1 (whole part), carry forward 0.6
     - \( 0.6 \times 2 = 1.2 \)  → 1 (whole part), carry forward 0.2
     - This gives us a repeating pattern of `0.01001...` in binary.
3. *Final Representation*: 
   - *Integer*: `10` (for 2)
   - *Fraction*: Limited to `3 bits` → `010` (approximating `0.3`)

Putting it all together:
- *Fixed-Point Representation*: In *Q2.3*, the representation of *2.3* would be
  `10.010`, which is `2` as integer part and `010` as fractional part.

### Fixed-Point Arithmetic Using 2.3

Now let's perform basic arithmetic operations using *2.3* as our model,
assuming we're working with fixed-point representation in *Q2.3*.

#### Addition

Let's add *2.3* (fixed representation `10.010`) and *1.5* (which we will convert).

1. *Convert 1.5 to Q2.3*:
   - *Integer Part*: `1` (binary `01`)
   - *Fractional Part*: `0.5` → In 3 bits → `100`
   - *Fixed Representation*: `01.100`

2. *Addition*:
   ```
          10.010  (= 2.3)
        + 01.100  (= 1.5)
        ---------
         11.110   (= 3.5 in fixed point)
   ```
   - This equals `3.5`, which is valid in our range since `3.5` can be represented.

#### Subtraction

Subtract *1.5* from *2.3*.

```
          10.010  (= 2.3)
        - 01.100  (= 1.5)
        ---------
          00.010  (= 0.5 in fixed point)
```
- The result is `0.5`, also valid.

#### Multiplication

Now let's multiply *2.3* and *1.5*.

1. *Fixed Representations*:
   - *2.3* = `10.010` (fixed)
   - *1.5* = `01.100` (fixed)

2. *Multiplication*:
   - Convert to integers (without considering fixed-point scaling):
   - $`2.3 \times 1.5 = 3.45`$

3. *Fixed-Point Result*:
   To convert back to fixed-point:
   - Multiply as integers: $` 10.010 \times 01.100 = 10.111100 `$
   - Right shift by 3 (since we have 3 fractional bits): `001.111` 
   - This is approximately `3.5` which fits our fixed-point range.

#### Division

To divide *2.3* by *1.5*.

1. *Fixed Representations*:
   - *2.3* = `10.010` (fixed)
   - *1.5* = `01.100` (fixed)

2. *Division*:
   $$\[
   \text{result} = \frac{2.3}{1.5} \approx 1.5333
   \]$$

3. *Fixed-Point Result*:
   To convert back to fixed-point:
   - Convert both to integer format:
   - Scale: $`\text{scale } = 8 `$ (for Q2.3)
   - Divide as integers and scale: 
   $$\[
   \text{result} = \frac{(10.010 \times 8)}{(01.100 \times 8)} = \frac{18.88}{12.0} = 1.57 \quad \text{(back to fixed-point)}
   \]$$

### C Code

Here's a simple implementation of fixed-point arithmetic using *2.3* as a model in C.

```c
#include <stdio.h>
#include <stdint.h>

// number of fractional bits for Q2.3
#define FRACTIONAL_BITS 3
#define SCALE (1 << FRACTIONAL_BITS)  // 2^3 = 8 for scaling

// fixed-point type: 8-bit signed integer
typedef int8_t fixed_point;

fixed_point float_to_fixed(float value) {
    return (fixed_point)(value * SCALE);
}

float fixed_to_float(fixed_point value) {
    return (float)value / SCALE;
}

fixed_point fixed_add(fixed_point a, fixed_point b) {
    return a + b;  // simple addition
}

fixed_point fixed_sub(fixed_point a, fixed_point b) {
    return a - b;  // simple subtraction
}

// multiplication of fixed-point numbers
fixed_point fixed_mul(fixed_point a, fixed_point b) {
    return (fixed_point)(((int16_t)a * (int16_t)b) >> FRACTIONAL_BITS); // right shift to scale down
}

// division of fixed-point numbers
fixed_point fixed_div(fixed_point a, fixed_point b) {
    return (fixed_point)((((int16_t)a << FRACTIONAL_BITS) + (b / 2)) / b); // scale numerator for precision
}

void print_fixed(fixed_point value) {
    printf("Fixed-point: %d (Float equivalent: %f)\n", value, fixed_to_float(value));
}

int main() {
    // represent 2.3 in fixed-point
    float num1 = 2.3;
    fixed_point fixed_num1 = float_to_fixed(num1);
    
    // another number, say 1.5
    float num2 = 1.5;
    fixed_point fixed_num2 = float_to_fixed(num2);
    
    printf("Original float: %f -> Fixed-point: ", num1);
    print_fixed(fixed_num1);
    
    printf("Original float: %f -> Fixed-point: ", num2);
    print_fixed(fixed_num2);
    
    fixed_point sum = fixed_add(fixed_num1, fixed_num2);
    printf("\nAddition:\n");
    print_fixed(sum);

    fixed_point diff = fixed_sub(fixed_num1, fixed_num2);
    printf("\nSubtraction:\n");
    print_fixed(diff);

    fixed_point product = fixed_mul(fixed_num1, fixed_num2);
    printf("\nMultiplication:\n");
    print_fixed(product);

    fixed_point quotient = fixed_div(fixed_num1, fixed_num2);
    printf("\nDivision:\n");
    print_fixed(quotient);

    return 0;
}
```
