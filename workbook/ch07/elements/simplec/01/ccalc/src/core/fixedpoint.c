// src/core/fixedpoint.c
#include "fixedpoint.h"

// 16.16 fixed point format: 16 bits for integer part, 16 bits for fractional part
typedef int32_t fixed_t;

// integer --> fixed point
fixed_t int_to_fixed(int i) {
    return i << 16;
}

// fixed point --> integer (truncates)
int fixed_to_int(fixed_t f) {
    return f >> 16;
}

// float --> fixed point
fixed_t float_to_fixed(float f) {
    return (fixed_t)(f * 65536.0f);
}

// fixed point --> float
float fixed_to_float(fixed_t f) {
    return f / 65536.0f;
}

// fixed-point addition
fixed_t fixed_add(fixed_t a, fixed_t b) {
    return a + b;
}

// fixed-point subtraction
fixed_t fixed_subtract(fixed_t a, fixed_t b) {
    return a - b;
}

// fixed-point multiplication
fixed_t fixed_multiply(fixed_t a, fixed_t b) {
    // use 64-bit arithmetic to avoid overflow
    int64_t result = (int64_t)a * (int64_t)b;
    return (fixed_t)(result >> 16);
}

// fixed-point division
fixed_t fixed_divide(fixed_t a, fixed_t b) {
    if (b == 0) {
        // division by zero
        return 0;
    }
    // pre-shift a to avoid overflow and maintain precision
    int64_t temp = (int64_t)a << 16;
    return (fixed_t)(temp / b);
}

// print fixed-point number
void fixed_print(fixed_t f) {
    int integer_part = fixed_to_int(f);
    int fractional_part = (int)(((f & 0xFFFF) * 10000) >> 16);
    printf("%d.%04d", integer_part, fractional_part);
}