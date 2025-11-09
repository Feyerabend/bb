#include <stdio.h>
#include <stdlib.h>

typedef struct TreapNode {
    int key, priority;
    struct TreapNode *left, *right;
} TreapNode;

TreapNode* newNode(int key) {
    TreapNode* node = (TreapNode*)malloc(sizeof(TreapNode));
    node->key = key;
    node->priority = rand() % 100;
    node->left = node->right = NULL;
    return node;
}

TreapNode* rotateRight(TreapNode* y) {
    TreapNode* x = y->left;
    y->left = x->right;
    x->right = y;
    return x;
}

TreapNode* rotateLeft(TreapNode* x) {
    TreapNode* y = x->right;
    x->right = y->left;
    y->left = x;
    return y;
}

TreapNode* insert(TreapNode* root, int key) {
    if (!root) return newNode(key);
    if (key < root->key) {
        root->left = insert(root->left, key);
        if (root->left->priority > root->priority)
            root = rotateRight(root);
    } else {
        root->right = insert(root->right, key);
        if (root->right->priority > root->priority)
            root = rotateLeft(root);
    }
    return root;
}

void inorder(TreapNode* root) {
    if (root) {
        inorder(root->left);
        printf("%d (%d) ", root->key, root->priority);
        inorder(root->right);
    }
}

int main() {
    TreapNode* root = NULL;
    int keys[] = {20, 15, 30, 25, 35, 10, 5};
    int n = sizeof(keys) / sizeof(keys[0]);
    
    for (int i = 0; i < n; i++)
        root = insert(root, keys[i]);
    
    inorder(root);  // inorder traversal of Treap
    return 0;
}
