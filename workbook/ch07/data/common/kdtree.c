#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int* point;  // point in k-dimensional space
    struct Node* left;
    struct Node* right;
} Node;

Node* create_node(int* point, int k) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->point = (int*)malloc(k * sizeof(int));
    for (int i = 0; i < k; i++) {
        new_node->point[i] = point[i];
    }
    new_node->left = new_node->right = NULL;
    return new_node;
}

Node* insert(Node* root, int* point, int depth, int k) {
    // base case: if tree empty, create new node
    if (root == NULL) {
        return create_node(point, k);
    }

    // calc current dimension (based on depth)
    int cd = depth % k;

    // if point should go to the left or right
    if (point[cd] < root->point[cd]) {
        root->left = insert(root->left, point, depth + 1, k);
    } else {
        root->right = insert(root->right, point, depth + 1, k);
    }

    return root;
}

void inorder_traversal(Node* root, int k) {
    if (root != NULL) {
        inorder_traversal(root->left, k);
        for (int i = 0; i < k; i++) {
            printf("%d ", root->point[i]);
        }
        printf("\n");
        inorder_traversal(root->right, k);
    }
}

Node* build_kd_tree(int points[][2], int n, int k) {
    Node* root = NULL;
    for (int i = 0; i < n; i++) {
        root = insert(root, points[i], 0, k);
    }
    return root;
}

int main() {
    int points[7][2] = {
        {3, 6},
        {17, 15},
        {13, 15},
        {6, 12},
        {9, 1},
        {2, 7},
        {10, 19}
    };
    int n = 7;
    int k = 2;

    Node* root = build_kd_tree(points, n, k);
    printf("K-D Tree Inorder Traversal:\n");
    inorder_traversal(root, k);

    return 0;
}
