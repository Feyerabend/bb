#ifndef HALF_ADDER_H
#define HALF_ADDER_H

#include "logical_gate.h"

typedef struct {
    LogicalGate xor;
    LogicalGate and;
} HalfAdderData;

int HalfAdder_compute(void* self, int a, int b, int cin, int* sum, int* cout);

#endif // HALF_ADDER_H