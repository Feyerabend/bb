#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// Structure to store suffixes and their indices
struct Suffix {
    int index;
    char *suffix;
};

// Comparator function for sorting suffixes
int compareSuffixes(const void *a, const void *b) {
    return strcmp(((struct Suffix *)a)->suffix, ((struct Suffix *)b)->suffix);
}

// Function to build the suffix array
int *buildSuffixArray(char *text, int n) {
    // Array to store suffixes and their indices
    struct Suffix suffixes[n];

    // Store all suffixes and their indices
    for (int i = 0; i < n; i++) {
        suffixes[i].index = i;
        suffixes[i].suffix = text + i;
    }

    // Sort the suffixes lexicographically
    qsort(suffixes, n, sizeof(struct Suffix), compareSuffixes);

    // Store the sorted indices in the suffix array
    int *suffixArray = (int *)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        suffixArray[i] = suffixes[i].index;
    }

    return suffixArray;
}

// Function to find the longest common prefix between two strings
int longestCommonPrefix(char *str1, char *str2) {
    int length = 0;
    while (*str1 && *str2 && *str1 == *str2) {
        length++;
        str1++;
        str2++;
    }
    return length;
}

// Function to find the longest repeated substring
char *longestRepeatedSubstring(char *text) {
    int n = strlen(text);

    // Build the suffix array
    int *suffixArray = buildSuffixArray(text, n);

    // Find the longest common prefix between adjacent suffixes
    int maxLength = 0;
    int startIndex = 0;

    for (int i = 0; i < n - 1; i++) {
        int lcp = longestCommonPrefix(text + suffixArray[i], text + suffixArray[i + 1]);
        if (lcp > maxLength) {
            maxLength = lcp;
            startIndex = suffixArray[i];
        }
    }

    // Free the suffix array
    free(suffixArray);

    // If no repeated substring is found, return an empty string
    if (maxLength == 0) {
        return "";
    }

    // Extract the longest repeated substring
    char *result = (char *)malloc((maxLength + 1) * sizeof(char));
    strncpy(result, text + startIndex, maxLength);
    result[maxLength] = '\0';

    return result;
}

int main() {
    char text[] = "abracadabra";

    printf("Text: %s\n", text);

    // Find the longest repeated substring
    char *result = longestRepeatedSubstring(text);

    if (strlen(result) > 0) {
        printf("Longest Repeated Substring: %s\n", result);
    } else {
        printf("No repeated substring found.\n");
    }

    // Free the result
    free(result);

    return 0;
}
