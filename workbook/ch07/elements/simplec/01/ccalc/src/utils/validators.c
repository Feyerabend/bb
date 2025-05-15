// src/utils/validators.c
#include "validators.h"
#include <ctype.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include <errno.h>

bool is_valid_number(const char* str) {
    if (str == NULL || *str == '\0') {
        return false;
    }
    
    // check for valid sign
    if (*str == '+' || *str == '-') {
        str++;
    }
    
    // check for at least one digit
    bool has_digit = false;
    bool has_decimal = false;
    
    while (*str) {
        if (isdigit((unsigned char)*str)) {
            has_digit = true;
        } else if (*str == '.' && !has_decimal) {
            has_decimal = true;
        } else {
            return false;
        }
        str++;
    }
    
    return has_digit;
}

bool parse_int(const char* str, int* result) {
    if (!is_valid_number(str)) {
        return false;
    }
    
    char* end;
    errno = 0;
    long val = strtol(str, &end, 10);
    
    if (errno != 0 || end == str || *end != '\0') {
        return false;
    }
    
    if (val > INT_MAX || val < INT_MIN) {
        return false;
    }
    
    *result = (int)val;
    return true;
}

bool is_valid_operation(const char* op) {
    if (op == NULL) {
        return false;
    }
    
    return (strcmp(op, "add") == 0 ||
            strcmp(op, "sub") == 0 ||
            strcmp(op, "mul") == 0 ||
            strcmp(op, "div") == 0 ||
            strcmp(op, "sin") == 0 ||
            strcmp(op, "cos") == 0 ||
            strcmp(op, "log") == 0);
}
