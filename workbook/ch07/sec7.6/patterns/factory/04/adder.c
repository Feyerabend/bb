#include "adder.h"
#include <stdlib.h>

typedef struct {
    void (*compute)(uint8_t a, uint8_t b, uint8_t cin, uint8_t *sum, uint8_t *cout);
} HalfAdder;

typedef struct {
    void (*compute)(uint8_t a, uint8_t b, uint8_t cin, uint8_t *sum, uint8_t *cout);
} FullAdder;

typedef struct {
    FullAdder *bit_adders[8];
} ByteAdder;

static void half_adder_compute(uint8_t a, uint8_t b, uint8_t cin, uint8_t *sum, uint8_t *cout) {
    uint8_t s = a ^ b;
    uint8_t c = a & b;

    *sum = s;
    *cout = c;
}

static void full_adder_compute(uint8_t a, uint8_t b, uint8_t cin, uint8_t *sum, uint8_t *cout) {
    uint8_t s1 = a ^ b;
    uint8_t c1 = a & b;
    uint8_t s = s1 ^ cin;
    uint8_t c2 = s1 & cin;
    *sum = s;
    *cout = c1 | c2;
}

static void byte_adder_compute(void *data, uint8_t a, uint8_t b, uint8_t cin, uint8_t *sum, uint8_t *cout) {
    ByteAdder *adder = (ByteAdder *)data;
    uint8_t carry = cin;
    uint8_t result = 0;

    for (int i = 0; i < 8; i++) {
        uint8_t bit_a = (a >> i) & 1;
        uint8_t bit_b = (b >> i) & 1;
        uint8_t bit_sum = 0, bit_carry = 0;

        adder->bit_adders[i]->compute(bit_a, bit_b, carry, &bit_sum, &bit_carry);

        result |= (bit_sum << i);
        carry = bit_carry;
    }

    *sum = result;
    *cout = carry;
}

Adder create_adder(AdderType type) {
    Adder adder = {0};

    if (type == HALF_ADDER) {
        HalfAdder *h = malloc(sizeof(HalfAdder));
        h->compute = half_adder_compute;
        adder.data = h;
        adder.compute = (void (*)(void *, uint8_t, uint8_t, uint8_t, uint8_t *, uint8_t *)) h->compute;
    } else if (type == FULL_ADDER) {
        FullAdder *f = malloc(sizeof(FullAdder));
        f->compute = full_adder_compute;
        adder.data = f;
        adder.compute = (void (*)(void *, uint8_t, uint8_t, uint8_t, uint8_t *, uint8_t *)) f->compute;
    } else if (type == BYTE_ADDER) {
        ByteAdder *b = malloc(sizeof(ByteAdder));
        for (int i = 0; i < 8; i++) {
            FullAdder *fa = malloc(sizeof(FullAdder));
            fa->compute = full_adder_compute;
            b->bit_adders[i] = fa;
        }
        adder.data = b;
        adder.compute = byte_adder_compute;
    }

    return adder;
}

void destroy_adder(Adder adder) {
    if (!adder.data) return;

    ByteAdder *b = (ByteAdder *)adder.data;
    if (adder.compute == byte_adder_compute) {
        for (int i = 0; i < 8; i++) {
            free(b->bit_adders[i]);
        }
        free(b);
    } else {
        free(adder.data);
    }
}

