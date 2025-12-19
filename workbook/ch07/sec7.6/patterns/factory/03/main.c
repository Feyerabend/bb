// main.c

#include <stdio.h>
#include "adder.h"

int main() {
    unsigned char a = 0xD5; // 213
    unsigned char b = 0x67; // 103
    unsigned char result = 0;
    int carry_in = 0;
    int carry_out = 0;

    Adder adders[8];
    for (int i = 0; i < 8; i++) {
        adders[i] = create_adder(FULL_ADDER);
    }

    for (int i = 0; i < 8; i++) {
        int bit_a = (a >> i) & 1;
        int bit_b = (b >> i) & 1;
        int sum_bit = 0;
        adders[i].compute(adders[i].data, bit_a, bit_b, carry_in, &sum_bit, &carry_out);
        result |= (sum_bit << i);
        carry_in = carry_out;
    }

    for (int i = 0; i < 8; i++) {
        destroy_adder(adders[i]);
    }

    printf("Operand A : 0x%02X (%d)\n", a, a);
    printf("Operand B : 0x%02X (%d)\n", b, b);
    printf("Sum       : 0x%02X (%d)\n", result, result);
    printf("Carry out : %d\n", carry_out);

    return 0;
}