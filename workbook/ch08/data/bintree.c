#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int key;
    struct Node *left, *right;
} Node;

Node *createNode(int key) {
    Node *node = (Node *)malloc(sizeof(Node));
    node->key = key;
    node->left = node->right = NULL;
    return node;
}

Node *insert(Node *root, int key) {
    if (!root)
        return createNode(key);
    if (key < root->key)
        root->left = insert(root->left, key);
    else
        root->right = insert(root->right, key);
    return root;
}

Node *search(Node *root, int key) {
    if (!root || root->key == key)
        return root;
    if (key < root->key)
        return search(root->left, key);
    return search(root->right, key);
}

void inorder(Node *root) {
    if (root) {
        inorder(root->left);
        printf("%d ", root->key);
        inorder(root->right);
    }
}

void preorder(Node *root) {
    if (root) {
        printf("%d ", root->key);
        preorder(root->left);
        preorder(root->right);
    }
}

void postorder(Node *root) {
    if (root) {
        postorder(root->left);
        postorder(root->right);
        printf("%d ", root->key);
    }
}

int height(Node *root) {
    if (!root)
        return 0;
    int leftHeight = height(root->left);
    int rightHeight = height(root->right);
    return (leftHeight > rightHeight ? leftHeight : rightHeight) + 1;
}

Node *minValueNode(Node *node) {
    Node *current = node;
    while (current && current->left)
        current = current->left;
    return current;
}

Node *deleteNode(Node *root, int key) {
    if (!root)
        return root;
    if (key < root->key)
        root->left = deleteNode(root->left, key);
    else if (key > root->key)
        root->right = deleteNode(root->right, key);
    else {
        if (!root->left) {
            Node *temp = root->right;
            free(root);
            return temp;
        } else if (!root->right) {
            Node *temp = root->left;
            free(root);
            return temp;
        }
        Node *temp = minValueNode(root->right);
        root->key = temp->key;
        root->right = deleteNode(root->right, temp->key);
    }
    return root;
}

void levelOrder(Node *root) {
    if (!root) return;
    Node *queue[100];
    int front = 0, rear = 0;
    queue[rear++] = root;
    while (front < rear) {
        Node *temp = queue[front++];
        printf("%d ", temp->key);
        if (temp->left)
            queue[rear++] = temp->left;
        if (temp->right)
            queue[rear++] = temp->right;
    }
}

int main() {
    Node *root = NULL;
    root = insert(root, 10);
    insert(root, 20);
    insert(root, 5);
    insert(root, 15);
    insert(root, 30);

    printf("Inorder Traversal:\n");
    inorder(root);
    printf("\nPreorder Traversal:\n");
    preorder(root);
    printf("\nPostorder Traversal:\n");
    postorder(root);
    printf("\nLevel-order Traversal:\n");
    levelOrder(root);
    printf("\nHeight of Tree: %d\n", height(root));

    root = deleteNode(root, 15);
    printf("\nInorder after deleting 15:\n");
    inorder(root);
    printf("\n");

    return 0;
}