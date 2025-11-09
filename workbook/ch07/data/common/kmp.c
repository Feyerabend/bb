#include <stdio.h>
#include <string.h>

// compute the prefix table (also called the "failure function")
void computePrefixTable(char *pattern, int patternLength, int *prefixTable) {
    int length = 0;  // length of the previous longest prefix suffix
    prefixTable[0] = 0;  // first value is always 0

    for (int i = 1; i < patternLength; ) {
        if (pattern[i] == pattern[length]) {
            length++;
            prefixTable[i] = length;
            i++;
        } else {
            if (length != 0) {
                length = prefixTable[length - 1];
            } else {
                prefixTable[i] = 0;
                i++;
            }
        }
    }
}

void KMPSearch(char *text, char *pattern) {
    int textLength = strlen(text);
    int patternLength = strlen(pattern);

    int prefixTable[patternLength];
    computePrefixTable(pattern, patternLength, prefixTable);

    int i = 0;  // index for text
    int j = 0;  // index for pattern

    while (i < textLength) {
        if (pattern[j] == text[i]) {
            i++;
            j++;
        }

        if (j == patternLength) {
            printf("Pattern found at index %d\n", i - j);
            j = prefixTable[j - 1];
        } else if (i < textLength && pattern[j] != text[i]) {
            if (j != 0) {
                j = prefixTable[j - 1];
            } else {
                i++;
            }
        }
    }
}

int main() {
    char text[] = "ABABDABACDABABCABAB";
    char pattern[] = "ABABCABAB";

    printf("Text: %s\n", text);
    printf("Pattern: %s\n", pattern);

    KMPSearch(text, pattern);

    return 0;
}
