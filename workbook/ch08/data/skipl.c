#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define MAX_LEVEL 16
#define P 0.5

typedef struct Node {
    int key;
    struct Node *forward[MAX_LEVEL + 1];
} Node;

typedef struct SkipList {
    int level;
    Node *header;
} SkipList;

Node* createNode(int key, int level) {
    Node *node = (Node *)malloc(sizeof(Node));
    node->key = key;
    for (int i = 0; i <= level; i++)
        node->forward[i] = NULL;
    return node;
}

SkipList* createSkipList() {
    SkipList *sl = (SkipList *)malloc(sizeof(SkipList));
    sl->level = 0;
    sl->header = createNode(INT_MIN, MAX_LEVEL);
    return sl;
}

int randomLevel() {
    int lvl = 0;
    while ((rand() / (double)RAND_MAX) < P && lvl < MAX_LEVEL)
        lvl++;
    return lvl;
}

void insert(SkipList *sl, int key) {
    Node *update[MAX_LEVEL + 1];
    Node *current = sl->header;

    for (int i = sl->level; i >= 0; i--) {
        while (current->forward[i] && current->forward[i]->key < key)
            current = current->forward[i];
        update[i] = current;
    }

    int level = randomLevel();
    if (level > sl->level) {
        for (int i = sl->level + 1; i <= level; i++)
            update[i] = sl->header;
        sl->level = level;
    }

    Node *new_node = createNode(key, level);
    for (int i = 0; i <= level; i++) {
        new_node->forward[i] = update[i]->forward[i];
        update[i]->forward[i] = new_node;
    }
}

int search(SkipList *sl, int key) {
    Node *current = sl->header;
    for (int i = sl->level; i >= 0; i--) {
        while (current->forward[i] && current->forward[i]->key < key)
            current = current->forward[i];
    }
    current = current->forward[0];
    return current && current->key == key;
}

void delete(SkipList *sl, int key) {
    Node *update[MAX_LEVEL + 1];
    Node *current = sl->header;

    for (int i = sl->level; i >= 0; i--) {
        while (current->forward[i] && current->forward[i]->key < key)
            current = current->forward[i];
        update[i] = current;
    }

    Node *target = current->forward[0];
    if (target && target->key == key) {
        for (int i = 0; i <= sl->level; i++) {
            if (update[i]->forward[i] != target)
                break;
            update[i]->forward[i] = target->forward[i];
        }
        free(target);

        while (sl->level > 0 && sl->header->forward[sl->level] == NULL)
            sl->level--;
    }
}

void display(SkipList *sl) {
    for (int i = 0; i <= sl->level; i++) {
        Node *node = sl->header->forward[i];
        printf("Level %d: ", i);
        while (node) {
            printf("%d -> ", node->key);
            node = node->forward[i];
        }
        printf("NULL\n");
    }
}

int main() {
    SkipList *sl = createSkipList();
    insert(sl, 3);
    insert(sl, 6);
    insert(sl, 7);
    insert(sl, 9);
    insert(sl, 12);
    
    display(sl);
    printf("Search 6: %s\n", search(sl, 6) ? "Found" : "Not Found");
    printf("Search 15: %s\n", search(sl, 15) ? "Found" : "Not Found");
    
    delete(sl, 6);
    display(sl);

    return 0;
}
