// src/core/fixedpoint.h
#ifndef FIXEDPOINT_H
#define FIXEDPOINT_H

#include <stdint.h>
#include <stdio.h>

typedef int32_t fixed_t;

fixed_t int_to_fixed(int i);
int fixed_to_int(fixed_t f);
fixed_t float_to_fixed(float f);
float fixed_to_float(fixed_t f);

fixed_t fixed_add(fixed_t a, fixed_t b);
fixed_t fixed_subtract(fixed_t a, fixed_t b);
fixed_t fixed_multiply(fixed_t a, fixed_t b);
fixed_t fixed_divide(fixed_t a, fixed_t b);

void fixed_print(fixed_t f);

#endif // FIXEDPOINT_H