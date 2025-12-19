#include "half_adder.h"

int HalfAdder_compute(void* self, int a, int b, int cin, int* sum, int* cout) {
    HalfAdderData* ha = (HalfAdderData*)self;
    *sum = ha->xor(a, b);
    *cout = ha->and(a, b);
    return 0;
}
