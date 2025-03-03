#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INITIAL_SIZE 8  
#define LOAD_FACTOR 0.75  

typedef struct Node {
    char* key;
    int value;
    struct Node* next;
} Node;

typedef struct HashTable {
    Node** table;
    int size;
    int count;
} HashTable;

unsigned int hash(const char* key, int size) {
    unsigned int hash = 5381;
    while (*key) {
        hash = ((hash << 5) + hash) + *key++; 
    }
    return hash % size;
}

Node* createNode(const char* key, int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (!newNode) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    newNode->key = strdup(key);
    newNode->value = value;
    newNode->next = NULL;
    return newNode;
}

HashTable* createTable(int size) {
    HashTable* ht = (HashTable*)malloc(sizeof(HashTable));
    if (!ht) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    ht->size = size;
    ht->count = 0;
    ht->table = (Node**)calloc(size, sizeof(Node*));
    if (!ht->table) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    return ht;
}

void insert(HashTable* ht, const char* key, int value);

void resize(HashTable* ht) {
    int newSize = ht->size * 2;
    Node** newTable = (Node**)calloc(newSize, sizeof(Node*));
    if (!newTable) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }

    Node** oldTable = ht->table;
    int oldSize = ht->size;
    ht->table = newTable;
    ht->size = newSize;
    ht->count = 0;

    for (int i = 0; i < oldSize; i++) {
        Node* current = oldTable[i];
        while (current) {
            insert(ht, current->key, current->value);
            Node* temp = current;
            current = current->next;
            free(temp->key);
            free(temp);
        }
    }
    free(oldTable);
}

void insert(HashTable* ht, const char* key, int value) {
    if ((float)ht->count / ht->size >= LOAD_FACTOR) {
        resize(ht);
    }

    unsigned int index = hash(key, ht->size);
    Node* current = ht->table[index];

    while (current) {
        if (strcmp(current->key, key) == 0) {
            current->value = value;
            return;
        }
        current = current->next;
    }

    Node* newNode = createNode(key, value);
    newNode->next = ht->table[index];
    ht->table[index] = newNode;
    ht->count++;
}

int get(HashTable* ht, const char* key) {
    unsigned int index = hash(key, ht->size);
    Node* current = ht->table[index];
    while (current) {
        if (strcmp(current->key, key) == 0) {
            return current->value;
        }
        current = current->next;
    }
    return -1;
}

void delete(HashTable* ht, const char* key) {
    unsigned int index = hash(key, ht->size);
    Node* current = ht->table[index];
    Node* prev = NULL;

    while (current) {
        if (strcmp(current->key, key) == 0) {
            if (prev) {
                prev->next = current->next;
            } else {
                ht->table[index] = current->next;
            }
            free(current->key);
            free(current);
            ht->count--;
            return;
        }
        prev = current;
        current = current->next;
    }
}

void display(HashTable* ht) {
    for (int i = 0; i < ht->size; i++) {
        printf("Index %d: ", i);
        Node* current = ht->table[i];
        while (current) {
            printf("(%s: %d) -> ", current->key, current->value);
            current = current->next;
        }
        printf("NULL\n");
    }
}

void freeTable(HashTable* ht) {
    for (int i = 0; i < ht->size; i++) {
        Node* current = ht->table[i];
        while (current) {
            Node* temp = current;
            current = current->next;
            free(temp->key);
            free(temp);
        }
    }
    free(ht->table);
    free(ht);
}

// exmaple
int main() {
    HashTable* ht = createTable(INITIAL_SIZE);
    insert(ht, "apple", 5);
    insert(ht, "banana", 10);
    insert(ht, "grape", 15);
    insert(ht, "orange", 20);
    insert(ht, "strawberry", 25);
    insert(ht, "mango", 30);
    insert(ht, "blueberry", 35);
    insert(ht, "kiwi", 40);
    insert(ht, "watermelon", 45);

    display(ht);
    printf("Value for 'apple': %d\n", get(ht, "apple"));
    printf("Value for 'banana': %d\n", get(ht, "banana"));

    delete(ht, "banana");
    printf("After deleting 'banana':\n");
    display(ht);

    freeTable(ht);
    return 0;
}