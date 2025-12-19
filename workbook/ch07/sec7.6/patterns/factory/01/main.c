#include <stdio.h>
#include "half_adder.h"

int main(void) {
    // Create Half-Adder via factory
    HalfAdderData adder = create_half_adder();

    // Example input bits
    int a = 1;
    int b = 1;

    // Compute sum and carry
    int sum = adder.xor_gate.apply(a, b);
    int carry = adder.and_gate.apply(a, b);

    // Display result
    printf("Input A = %d, B = %d\n", a, b);
    printf("Sum = %d\n", sum);
    printf("Carry = %d\n", carry);

    return 0;
}