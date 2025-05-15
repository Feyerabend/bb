// src/core/advanced.c
#include "advanced.h"
#include <math.h>

double sine(double angle) {
    return sin(angle);
}

double cosine(double angle) {
    return cos(angle);
}

double logarithm(double value, double base) {
    if (value <= 0 || base <= 0 || base == 1) {
        // in real code: you'd handle these errors properly
        return 0;
    }
    return log(value) / log(base);
}
