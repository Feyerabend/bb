#ifndef HALF_ADDER_H
#define HALF_ADDER_H

#include "logical_gate.h"

// HalfAdderData: Composes logical gates to implement a half-adder circuit
typedef struct {
    LogicalGate xor_gate;  // Computes sum bit
    LogicalGate and_gate;  // Computes carry bit
} HalfAdderData;

// Factory function: Creates a HalfAdderData instance with wired gates
HalfAdderData create_half_adder(void);

#endif // HALF_ADDER_H