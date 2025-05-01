#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#define SIZE 1000 // size of bit array
#define HASH_COUNT 3 // num of hash functions

// hash function 1 (simple DJB2)
unsigned long hash1(char *str) {
    unsigned long hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash;
}

// hash function 2 (a simple variation)
unsigned long hash2(char *str) {
    unsigned long hash = 0;
    int c;
    while ((c = *str++)) {
        hash = (hash * 31) + c;
    }
    return hash;
}

// hash function 3 (another simple hash function)
unsigned long hash3(char *str) {
    unsigned long hash = 0;
    int c;
    while ((c = *str++)) {
        hash = (hash * 53) + c;
    }
    return hash;
}

// Bloom Filter structure
typedef struct {
    unsigned char bit_array[SIZE];
} BloomFilter;

// init Bloom Filter
void init_bloom_filter(BloomFilter *bf) {
    memset(bf->bit_array, 0, SIZE);
}

// add item to Bloom Filter
void add(BloomFilter *bf, char *item) {
    unsigned long h1 = hash1(item) % SIZE;
    unsigned long h2 = hash2(item) % SIZE;
    unsigned long h3 = hash3(item) % SIZE;

    bf->bit_array[h1] = 1;
    bf->bit_array[h2] = 1;
    bf->bit_array[h3] = 1;
}

// check if item is in Bloom Filter
int check(BloomFilter *bf, char *item) {
    unsigned long h1 = hash1(item) % SIZE;
    unsigned long h2 = hash2(item) % SIZE;
    unsigned long h3 = hash3(item) % SIZE;

    if (bf->bit_array[h1] == 0 || bf->bit_array[h2] == 0 || bf->bit_array[h3] == 0)
        return 0; // not in set
    return 1; // possibly in set
}

int main() {
    BloomFilter bf;
    init_bloom_filter(&bf);

    add(&bf, "apple");
    add(&bf, "banana");

    printf("Check apple: %d\n", check(&bf, "apple"));    // 1 (true)
    printf("Check banana: %d\n", check(&bf, "banana"));  // 1 (true)
    printf("Check grape: %d\n", check(&bf, "grape"));    // 0 (false, but might return true due to false positive)

    return 0;
}
