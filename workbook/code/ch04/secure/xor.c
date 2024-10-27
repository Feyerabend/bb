#include <stdio.h>
#include <string.h>

void xorEncryptDecrypt(char *input, const char *key, size_t len) {
    size_t key_len = strlen(key);
    for (size_t i = 0; i < len; i++) {
        input[i] ^= key[i % key_len];
    }
}

void printHex(const char *data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        printf("%02X ", (unsigned char)data[i]);
    }
    printf("\n");
}

int main() {
    char message[] = "SecureMessage";
    const char key[] = "key";
    size_t message_len = strlen(message);

    printf("Original Message: %s\n", message);
    
    // Encrypt the message
    xorEncryptDecrypt(message, key, message_len);
    printf("Encrypted Message in Hex: ");
    printHex(message, message_len);  // Display encrypted message in hex format

    // Decrypt the message
    xorEncryptDecrypt(message, key, message_len);
    printf("Decrypted Message: %s\n", message);  // Should match the original message

    return 0;
}