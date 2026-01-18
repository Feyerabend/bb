#ifndef LOGICAL_GATE_H
#define LOGICAL_GATE_H

// LogicalGate: Encapsulates a binary logic gate function (Strategy)
typedef struct {
    int (*apply)(int a, int b);
} LogicalGate;

#endif // LOGICAL_GATE_H