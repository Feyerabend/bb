// gate.c

#include <stdlib.h>
#include "gate.h"

typedef struct {
    GateType type;
} GateData;

static int gate_compute(void *data, int a, int b) {
    GateData *d = (GateData *)data;
    switch (d->type) {
        case XOR_GATE: return a ^ b;
        case AND_GATE: return a & b;
        case OR_GATE:  return a | b;
        default: return 0;
    }
}

LogicalGate create_gate(GateType type) {
    LogicalGate gate;
    GateData *data = malloc(sizeof(GateData));
    data->type = type;
    gate.data = data;
    gate.compute = gate_compute;
    return gate;
}

void destroy_gate(LogicalGate gate) {
    free(gate.data);
}