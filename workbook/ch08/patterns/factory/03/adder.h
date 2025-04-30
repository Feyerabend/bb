// adder.h

#ifndef ADDER_H
#define ADDER_H

typedef enum {
    HALF_ADDER,
    FULL_ADDER
} AdderType;

typedef struct {
    void *data;
    void (*compute)(void *self, int a, int b, int cin, int *sum, int *cout);
} Adder;

Adder create_adder(AdderType type);
void destroy_adder(Adder adder);

#endif // ADDER_H