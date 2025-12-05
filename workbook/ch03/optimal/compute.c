#include <stdio.h>
#include <math.h>

double compute(int a, int b) {
    return pow(a, 2) + pow(a, 2) + b;
}

double compute_opt(int a, int b) {
    double a_squared = pow(a, 2);
    return a_squared + a_squared + b;
}


int square(int x) {
    return x * x;
}

int compute2(int x, int y) {
    return square(x) + square(y);
}

int compute2_opt(int x, int y) {
    return (x * x) + (y * y);
}

