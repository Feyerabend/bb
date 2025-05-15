// src/utils/validators.h
#ifndef VALIDATORS_H
#define VALIDATORS_H

#include <stdbool.h>

bool is_valid_number(const char* str);
bool parse_int(const char* str, int* result);
bool is_valid_operation(const char* op);

#endif // VALIDATORS_H