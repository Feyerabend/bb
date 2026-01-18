// adder.c

#include <stdlib.h>
#include "adder.h"

// HalfAdder struct
typedef struct {
    void (*compute)(void *self, int a, int b, int cin, int *sum, int *cout);
} HalfAdder;

// FullAdder struct
typedef struct {
    void (*compute)(void *self, int a, int b, int cin, int *sum, int *cout);
} FullAdder;

// HalfAdder compute
void half_adder_compute(void *self, int a, int b, int cin, int *sum, int *cout) {
    *sum = a ^ b;
    *cout = a & b;
}

// FullAdder compute
void full_adder_compute(void *self, int a, int b, int cin, int *sum, int *cout) {
    int sum1 = a ^ b;
    int carry1 = a & b;
    *sum = sum1 ^ cin;
    int carry2 = sum1 & cin;
    *cout = carry1 | carry2;
}

Adder create_adder(AdderType type) {
    Adder adder;
    if (type == HALF_ADDER) {
        HalfAdder *ha = malloc(sizeof(HalfAdder));
        ha->compute = half_adder_compute;
        adder.data = ha;
        adder.compute = half_adder_compute;
    } else {
        FullAdder *fa = malloc(sizeof(FullAdder));
        fa->compute = full_adder_compute;
        adder.data = fa;
        adder.compute = full_adder_compute;
    }
    return adder;
}

void destroy_adder(Adder adder) {
    free(adder.data);
}