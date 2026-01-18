#include <stdio.h>
#include <stdlib.h>

#define T 2  // minimum degree (order of tree)

typedef struct BTreeNode {
    int keys[2 * T - 1]; 
    struct BTreeNode *children[2 * T];
    int num_keys;  
    int leaf;      
} BTreeNode;

typedef struct {
    BTreeNode *root;
} BTree;

BTreeNode *createNode(int leaf) {
    BTreeNode *node = (BTreeNode *)malloc(sizeof(BTreeNode));
    node->num_keys = 0;
    node->leaf = leaf;
    for (int i = 0; i < 2 * T; i++)
        node->children[i] = NULL;
    return node;
}

BTreeNode *search(BTreeNode *node, int key) {
    if (node == NULL) return NULL;
    int i = 0;
    while (i < node->num_keys && key > node->keys[i])
        i++;

    if (i < node->num_keys && key == node->keys[i])
        return node;

    if (node->leaf)
        return NULL;

    return search(node->children[i], key);
}

void splitChild(BTreeNode *parent, int i) {
    BTreeNode *node = parent->children[i];
    BTreeNode *new_node = createNode(node->leaf);
    new_node->num_keys = T - 1;

    for (int j = 0; j < T - 1; j++)
        new_node->keys[j] = node->keys[j + T];

    if (!node->leaf) {
        for (int j = 0; j < T; j++)
            new_node->children[j] = node->children[j + T];
    }

    node->num_keys = T - 1;

    for (int j = parent->num_keys; j >= i + 1; j--)
        parent->children[j + 1] = parent->children[j];

    parent->children[i + 1] = new_node;

    for (int j = parent->num_keys - 1; j >= i; j--)
        parent->keys[j + 1] = parent->keys[j];

    parent->keys[i] = node->keys[T - 1];
    parent->num_keys++;
}

void insertNonFull(BTreeNode *node, int key) {
    int i = node->num_keys - 1;

    if (node->leaf) {
        while (i >= 0 && key < node->keys[i]) {
            node->keys[i + 1] = node->keys[i];
            i--;
        }
        node->keys[i + 1] = key;
        node->num_keys++;
    } else {
        while (i >= 0 && key < node->keys[i])
            i--;
        i++;

        if (node->children[i]->num_keys == (2 * T - 1)) {
            splitChild(node, i);
            if (key > node->keys[i])
                i++;
        }
        insertNonFull(node->children[i], key);
    }
}

void insert(BTree *tree, int key) {
    BTreeNode *root = tree->root;
    if (root->num_keys == (2 * T - 1)) {
        BTreeNode *new_root = createNode(0);
        new_root->children[0] = root;
        tree->root = new_root;
        splitChild(new_root, 0);
    }
    insertNonFull(tree->root, key);
}

void traverse(BTreeNode *node) {
    if (node == NULL) return;
    for (int i = 0; i < node->num_keys; i++) {
        if (!node->leaf)
            traverse(node->children[i]);
        printf("%d ", node->keys[i]);
    }
    if (!node->leaf)
        traverse(node->children[node->num_keys]);
}

int main() {
    BTree tree;
    tree.root = createNode(1);

    int keys[] = {10, 20, 5, 6, 12, 30, 7, 17};
    for (int i = 0; i < 8; i++)
        insert(&tree, keys[i]);

    printf("B-Tree traversal:\n");
    traverse(tree.root);
    printf("\n");

    return 0;
}
