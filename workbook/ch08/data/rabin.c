#include <stdio.h>
#include <string.h>

#define PRIME 101

long power(int base, int exponent) {
    long result = 1;
    for (int i = 0; i < exponent; i++) {
        result = (result * base) % PRIME;
    }
    return result;
}

long calculateHash(char *str, int length) {
    long hash = 0;
    for (int i = 0; i < length; i++) {
        hash = (hash * 256 + str[i]) % PRIME;
    }
    return hash;
}

long recalculateHash(char *str, int oldIndex, int newIndex, long oldHash, int patternLength) {
    long newHash = (oldHash - str[oldIndex] * power(256, patternLength - 1)) % PRIME;
    newHash = (newHash * 256 + str[newIndex]) % PRIME;
    return newHash < 0 ? newHash + PRIME : newHash;
}

void rabinKarpSearch(char *text, char *pattern) {
    int textLength = strlen(text);
    int patternLength = strlen(pattern);

    long patternHash = calculateHash(pattern, patternLength);
    long textHash = calculateHash(text, patternLength);

    for (int i = 0; i <= textLength - patternLength; i++) {
        if (patternHash == textHash) {
            int j;
            for (j = 0; j < patternLength; j++) {
                if (text[i + j] != pattern[j]) {
                    break;
                }
            }
            if (j == patternLength) {
                printf("Pattern found at index %d\n", i);
            }
        }

        if (i < textLength - patternLength) {
            textHash = recalculateHash(text, i, i + patternLength, textHash, patternLength);
        }
    }
}

int main() {
    char text[] = "ABABDABACDABABCABAB";
    char pattern[] = "ABABCABAB";

    printf("Text: %s\n", text);
    printf("Pattern: %s\n", pattern);

    rabinKarpSearch(text, pattern);

    return 0;
}
