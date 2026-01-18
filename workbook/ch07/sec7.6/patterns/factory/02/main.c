#include <stdio.h>
#include <stdlib.h>
#include "gates.h"
#include "half_adder.h"
#include "full_adder.h"

// Factory
typedef struct {
    int (*compute)(void* self, int a, int b, int cin, int* sum, int* cout);
    void* data;
} Adder;

typedef enum { HALF_ADDER, FULL_ADDER } AdderType;

Adder create_adder(AdderType type) {
    Adder adder;

    switch(type) {
        case HALF_ADDER: {
            HalfAdderData* data = malloc(sizeof(HalfAdderData));
            data->xor = XOR;
            data->and = AND;
            adder.data = data;
            adder.compute = HalfAdder_compute;
            break;
        }
        case FULL_ADDER: {
            FullAdderData* data = malloc(sizeof(FullAdderData));
            data->xor1 = XOR;
            data->xor2 = XOR;
            data->and1 = AND;
            data->and2 = AND;
            data->or = OR;
            adder.data = data;
            adder.compute = FullAdder_compute;
            break;
        }
    }

    return adder;
}

int main() {
    // Half Adder test
    Adder half_adder = create_adder(HALF_ADDER);
    int sum, cout;
    half_adder.compute(half_adder.data, 1, 1, 0, &sum, &cout);
    printf("Half Adder (1 + 1): Sum = %d, Carry = %d\n", sum, cout);

    // Full Adder test
    Adder full_adder = create_adder(FULL_ADDER);
    printf("\nFull Adder Test (a=1, b=1, cin=1)\n");
    full_adder.compute(full_adder.data, 1, 1, 1, &sum, &cout);
    printf("Inputs: a=1, b=1, cin=1\n");
    printf("Result: Sum = %d, Carry = %d\n", sum, cout);

    // Cleanup
    free(half_adder.data);
    free(full_adder.data);

    return 0;
}