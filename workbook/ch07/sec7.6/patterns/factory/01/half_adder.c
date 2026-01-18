#include "half_adder.h"
#include "gates.h"

// Factory function implementation
HalfAdderData create_half_adder(void) {
    HalfAdderData data = {
        .xor_gate = { .apply = XOR },
        .and_gate = { .apply = AND }
    };
    return data;
}