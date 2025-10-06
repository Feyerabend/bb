#include <stdio.h>

int mod_exp(int base, int exp, int mod) {
    int result = 1;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}
int main() {
    // Small demonstration parameters (use large primes in practice)
    int p = 61, q = 53;
    int n = p * q; // n = 3233
    int e = 17; // public exponent
    int d = 2753; // private exponent (precomputed)
    int message = 65; // message as integer
    printf("RSA Demonstration\n");
    printf("Public Key: (e=%d, n=%d)\n", e, n);
    printf("Private Key: (d=%d, n=%d)\n", d, n);
    // Encryption with public key
    int ciphertext = mod_exp(message, e, n);
    printf("Original: %d\n", message);
    printf("Encrypted: %d\n", ciphertext);
    // Decryption with private key
    int decrypted = mod_exp(ciphertext, d, n);
    printf("Decrypted: %d\n", decrypted);
    return 0;
}
// Compile with: gcc -o demo demo.c -std=c17