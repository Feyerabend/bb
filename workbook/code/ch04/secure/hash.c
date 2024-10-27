#include <stdio.h>
#include <string.h>

unsigned int simpleHash(const char *str) {
    unsigned int hash = 0;
    while (*str) {
        hash += *str++;
    }
    return hash;
}

int main() {
    const char *data = "IntegrityCheck";
    unsigned int hash = simpleHash(data);

    printf("Original Data: %s\n", data);
    printf("Data Integrity Hash: %u\n", hash);

    const char *newData = "IntegrityChanged";
    unsigned int newHash = simpleHash(newData);

    if (hash == newHash) {
        printf("Data is intact.\n");
    } else {
        printf("Data integrity has been compromised!\n");
    }

    return 0;
}