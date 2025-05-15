// src/ui/cli.c
#include "cli.h"
#include "../core/arithmetic.h"
#include "../core/advanced.h"
#include "../core/fixedpoint.h"
#include "../utils/validators.h"
#include "../utils/logger.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void print_usage(const char* program_name) {
    printf("Usage: %s operation [arguments]\n", program_name);
    printf("Operations:\n");
    printf("  add a b        - Add two integers\n");
    printf("  sub a b        - Subtract b from a\n");
    printf("  mul a b        - Multiply two integers\n");
    printf("  div a b        - Divide a by b\n");
    printf("  sin angle      - Calculate sine of angle (in radians)\n");
    printf("  cos angle      - Calculate cosine of angle (in radians)\n");
    printf("  log value base - Calculate logarithm of value with given base\n");
    printf("  fixed op a b   - Perform operation (add,sub,mul,div) using 16.16 fixed-point\n");
}

bool process_args(int argc, char* argv[]) {
    if (argc < 2) {
        LOG_ERROR("No operation specified");
        print_usage(argv[0]);
        return false;
    }
    
    const char* operation = argv[1];
    
    if (!is_valid_operation(operation) && strcmp(operation, "fixed") != 0) {
        LOG_ERROR("Invalid operation: %s", operation);
        print_usage(argv[0]);
        return false;
    }
    
    // basic arithmetic
    if (strcmp(operation, "add") == 0 || 
        strcmp(operation, "sub") == 0 || 
        strcmp(operation, "mul") == 0 || 
        strcmp(operation, "div") == 0) {
        
        if (argc != 4) {
            LOG_ERROR("Arithmetic operations require exactly 2 arguments");
            return false;
        }
        
        int a, b, result;
        if (!parse_int(argv[2], &a) || !parse_int(argv[3], &b)) {
            LOG_ERROR("Invalid number format");
            return false;
        }
        
        if (strcmp(operation, "add") == 0) {
            result = add(a, b);
            printf("%d + %d = %d\n", a, b, result);
        } else if (strcmp(operation, "sub") == 0) {
            result = subtract(a, b);
            printf("%d - %d = %d\n", a, b, result);
        } else if (strcmp(operation, "mul") == 0) {
            result = multiply(a, b);
            printf("%d * %d = %d\n", a, b, result);
        } else if (strcmp(operation, "div") == 0) {
            if (b == 0) {
                LOG_ERROR("Division by zero");
                return false;
            }
            result = divide(a, b);
            printf("%d / %d = %d\n", a, b, result);
        }
        
        return true;
    }
    
    // advanced functions
    if (strcmp(operation, "sin") == 0 || strcmp(operation, "cos") == 0) {
        if (argc != 3) {
            LOG_ERROR("Trigonometric operations require exactly 1 argument");
            return false;
        }
        
        double angle = atof(argv[2]);
        double result;
        
        if (strcmp(operation, "sin") == 0) {
            result = sine(angle);
            printf("sin(%f) = %f\n", angle, result);
        } else {
            result = cosine(angle);
            printf("cos(%f) = %f\n", angle, result);
        }
        
        return true;
    }
    
    if (strcmp(operation, "log") == 0) {
        if (argc != 4) {
            LOG_ERROR("Logarithm operation requires exactly 2 arguments");
            return false;
        }
        
        double value = atof(argv[2]);
        double base = atof(argv[3]);
        
        if (value <= 0 || base <= 0 || base == 1) {
            LOG_ERROR("Invalid arguments for logarithm");
            return false;
        }
        
        double result = logarithm(value, base);
        printf("log_%f(%f) = %f\n", base, value, result);
        
        return true;
    }
    
    // fixed-point operations
    if (strcmp(operation, "fixed") == 0) {
        if (argc != 5) {
            LOG_ERROR("Fixed-point operation requires 3 arguments: operation and two numbers");
            return false;
        }
        
        const char* fixed_op = argv[2];
        float a = atof(argv[3]);
        float b = atof(argv[4]);
        
        fixed_t fixed_a = float_to_fixed(a);
        fixed_t fixed_b = float_to_fixed(b);
        fixed_t result;
        
        if (strcmp(fixed_op, "add") == 0) {
            result = fixed_add(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" + ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else if (strcmp(fixed_op, "sub") == 0) {
            result = fixed_subtract(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" - ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else if (strcmp(fixed_op, "mul") == 0) {
            result = fixed_multiply(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" * ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else if (strcmp(fixed_op, "div") == 0) {
            if (b == 0) {
                LOG_ERROR("Division by zero");
                return false;
            }
            result = fixed_divide(fixed_a, fixed_b);
            printf("Fixed-point: ");
            fixed_print(fixed_a);
            printf(" / ");
            fixed_print(fixed_b);
            printf(" = ");
            fixed_print(result);
            printf("\n");
        } else {
            LOG_ERROR("Invalid fixed-point operation: %s", fixed_op);
            return false;
        }
        
        return true;
    }
    
    return false;
}
