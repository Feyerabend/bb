#ifndef ADDER_H
#define ADDER_H

#include <stdint.h>

typedef enum {
    HALF_ADDER,
    FULL_ADDER,
    BYTE_ADDER
} AdderType;

typedef struct {
    void *data;
    void (*compute)(void *data, uint8_t a, uint8_t b, uint8_t cin, uint8_t *sum, uint8_t *cout);
} Adder;

Adder create_adder(AdderType type);
void destroy_adder(Adder adder);

#endif // ADDER_H