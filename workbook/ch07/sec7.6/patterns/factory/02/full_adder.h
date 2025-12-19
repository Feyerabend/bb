#ifndef FULL_ADDER_H
#define FULL_ADDER_H

#include "logical_gate.h"

typedef struct {
    LogicalGate xor1;
    LogicalGate xor2;
    LogicalGate and1;
    LogicalGate and2;
    LogicalGate or;
} FullAdderData;

int FullAdder_compute(void* self, int a, int b, int cin, int* sum, int* cout);

#endif // FULL_ADDER_H