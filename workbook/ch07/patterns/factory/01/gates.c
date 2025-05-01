#include "gates.h"

// XOR gate implementation: returns a XOR b
int XOR(int a, int b) {
    return (a || b) && !(a && b);
}

// AND gate implementation: returns a AND b
int AND(int a, int b) {
    return a && b;
}