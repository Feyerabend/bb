// gate.h

#ifndef GATE_H
#define GATE_H

typedef enum {
    XOR_GATE,
    AND_GATE,
    OR_GATE
} GateType;

typedef struct {
    void *data;
    int (*compute)(void *data, int a, int b);
} LogicalGate;

LogicalGate create_gate(GateType type);
void destroy_gate(LogicalGate gate);

#endif // GATE_H