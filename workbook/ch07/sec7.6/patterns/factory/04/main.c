#include <stdio.h>
#include "adder.h"

int main() {
    uint8_t a = 0xD5; // 213 = 0b11010101
    uint8_t b = 0x67; // 103 = 0b01100111
    uint8_t sum = 0, cout = 0;

    Adder byte_adder = create_adder(BYTE_ADDER);
    byte_adder.compute(byte_adder.data, a, b, 0, &sum, &cout);

    printf("Operand A : 0x%02X (%d)\n", a, a);
    printf("Operand B : 0x%02X (%d)\n", b, b);
    printf("Sum       : 0x%02X (%d)\n", sum, sum);
    printf("Carry out : %d\n", cout);

    destroy_adder(byte_adder);
    return 0;
}
