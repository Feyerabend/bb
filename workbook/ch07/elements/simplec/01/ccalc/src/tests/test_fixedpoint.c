// tests/test_fixedpoint.c
#include "../src/core/fixedpoint.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <math.h>

#define EPSILON 0.0001

void test_conversions() {
    printf("Testing fixed-point conversions...\n");
    
    // Test integer conversions
    fixed_t a = int_to_fixed(5);
    assert(fixed_to_int(a) == 5);
    
    // Test float conversions
    fixed_t b = float_to_fixed(3.25f);
    float b_float = fixed_to_float(b);
    assert(fabs(b_float - 3.25f) < EPSILON);
    
    // Test negative values
    fixed_t c = int_to_fixed(-10);
    assert(fixed_to_int(c) == -10);
    
    fixed_t d = float_to_fixed(-7.5f);
    float d_float = fixed_to_float(d);
    assert(fabs(d_float - (-7.5f)) < EPSILON);
    
    printf("Conversion tests passed!\n");
}

void test_operations() {
    printf("Testing fixed-point operations...\n");
    
    // Test addition
    fixed_t a = float_to_fixed(5.25f);
    fixed_t b = float_to_fixed(3.75f);
    
    fixed_t sum = fixed_add(a, b);
    float sum_float = fixed_to_float(sum);
    assert(fabs(sum_float - 9.0f) < EPSILON);
    
    // Test subtraction
    fixed_t diff = fixed_subtract(a, b);
    float diff_float = fixed_to_float(diff);
    assert(fabs(diff_float - 1.5f) < EPSILON);
    
    // Test multiplication
    fixed_t prod = fixed_multiply(a, b);
    float prod_float = fixed_to_float(prod);
    assert(fabs(prod_float - 19.6875f) < EPSILON);
    
    // Test division
    fixed_t quot = fixed_divide(a, b);
    float quot_float = fixed_to_float(quot);
    assert(fabs(quot_float - 1.4f) < EPSILON);
    
    printf("Operation tests passed!\n");
}

int main() {
    printf("Running fixed-point tests...\n");
    
    test_conversions();
    test_operations();
    
    printf("All fixed-point tests passed!\n");
    
    return 0;
}