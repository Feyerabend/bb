#include "full_adder.h"

int FullAdder_compute(void* self, int a, int b, int cin, int* sum, int* cout) {
    FullAdderData* fa = (FullAdderData*)self;

    int xor1 = fa->xor1(a, b);
    int and1 = fa->and1(a, b);
    int and2 = fa->and2(xor1, cin);

    *sum = fa->xor2(xor1, cin);
    *cout = fa->or(and1, and2);

    return 0;
}