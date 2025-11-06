#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define ALPHABET_SIZE 26

typedef struct TrieNode {
    struct TrieNode *children[ALPHABET_SIZE];
    bool is_end_of_word;
} TrieNode;

TrieNode* create_node() {
    TrieNode* node = (TrieNode*)malloc(sizeof(TrieNode));
    node->is_end_of_word = false;
    for (int i = 0; i < ALPHABET_SIZE; i++)
        node->children[i] = NULL;
    return node;
}

typedef struct Trie {
    TrieNode *root;
} Trie;

Trie* create_trie() {
    Trie* trie = (Trie*)malloc(sizeof(Trie));
    trie->root = create_node();
    return trie;
}

void insert(Trie* trie, const char* word) {
    TrieNode* node = trie->root;
    while (*word) {
        int index = *word - 'a';
        if (!node->children[index])
            node->children[index] = create_node();
        node = node->children[index];
        word++;
    }
    node->is_end_of_word = true;
}

bool search(Trie* trie, const char* word) {
    TrieNode* node = trie->root;
    while (*word) {
        int index = *word - 'a';
        if (!node->children[index])
            return false;
        node = node->children[index];
        word++;
    }
    return node->is_end_of_word;
}

bool starts_with(Trie* trie, const char* prefix) {
    TrieNode* node = trie->root;
    while (*prefix) {
        int index = *prefix - 'a';
        if (!node->children[index])
            return false;
        node = node->children[index];
        prefix++;
    }
    return true;
}


int main() {
    Trie* trie = create_trie();
    insert(trie, "hello");
    insert(trie, "world");
    printf("Search 'hello': %s\n", search(trie, "hello") ? "True" : "False");
    printf("Search 'hell': %s\n", search(trie, "hell") ? "True" : "False");
    printf("Starts with 'wor': %s\n", starts_with(trie, "wor") ? "True" : "False");
    return 0;
}
