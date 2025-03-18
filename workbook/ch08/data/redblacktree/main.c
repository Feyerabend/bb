#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// colors for Red-Black Tree
#define RED 0
#define BLACK 1

// Red-Black Tree Node
typedef struct RedBlackTreeNode {
    char *key;
    char *value;
    int color;
    struct RedBlackTreeNode *left, *right, *parent;
} RedBlackTreeNode;

// Red-Black Tree Structure
typedef struct {
    RedBlackTreeNode *root;
    RedBlackTreeNode *nil; // sentinel node for leaves
} RedBlackTree;


RedBlackTreeNode *createNode(char *key, char *value) {
    RedBlackTreeNode *node = (RedBlackTreeNode *)malloc(sizeof(RedBlackTreeNode));
    node->key = strdup(key);
    node->value = strdup(value);
    node->color = RED;
    node->left = node->right = node->parent = NULL;
    return node;
}

RedBlackTree *createRedBlackTree() {
    RedBlackTree *tree = (RedBlackTree *)malloc(sizeof(RedBlackTree));
    tree->nil = createNode("Nil", "Nil");
    tree->nil->color = BLACK;
    tree->root = tree->nil;
    return tree;
}

int comp(char *key1, char *key2) {
    return strcmp(key1, key2);
}

void inorderWalk(RedBlackTreeNode *x, RedBlackTreeNode *nil) {
    if (x != nil) {
        inorderWalk(x->left, nil);
        printf("Key: %s, Value: %s\n", x->key, x->value);
        inorderWalk(x->right, nil);
    }
}

void rotateLeft(RedBlackTree *tree, RedBlackTreeNode *x) {
    RedBlackTreeNode *y = x->right;
    x->right = y->left;
    if (y->left != tree->nil) {
        y->left->parent = x;
    }
    y->parent = x->parent;
    if (x->parent == tree->nil) {
        tree->root = y;
    } else if (x == x->parent->left) {
        x->parent->left = y;
    } else {
        x->parent->right = y;
    }
    y->left = x;
    x->parent = y;
}

void rotateRight(RedBlackTree *tree, RedBlackTreeNode *y) {
    RedBlackTreeNode *x = y->left;
    y->left = x->right;
    if (x->right != tree->nil) {
        x->right->parent = y;
    }
    x->parent = y->parent;
    if (y->parent == tree->nil) {
        tree->root = x;
    } else if (y == y->parent->left) {
        y->parent->left = x;
    } else {
        y->parent->right = x;
    }
    x->right = y;
    y->parent = x;
}

void insertFixup(RedBlackTree *tree, RedBlackTreeNode *z) {
    while (z->parent->color == RED) {
        if (z->parent == z->parent->parent->left) {
            RedBlackTreeNode *y = z->parent->parent->right;
            if (y->color == RED) {
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->right) {
                    z = z->parent;
                    rotateLeft(tree, z);
                }
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                rotateRight(tree, z->parent->parent);
            }
        } else {
            RedBlackTreeNode *y = z->parent->parent->left;
            if (y->color == RED) {
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->left) {
                    z = z->parent;
                    rotateRight(tree, z);
                }
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                rotateLeft(tree, z->parent->parent);
            }
        }
    }
    tree->root->color = BLACK;
}

void insert(RedBlackTree *tree, RedBlackTreeNode *z) {
    RedBlackTreeNode *y = tree->nil;
    RedBlackTreeNode *x = tree->root;
    while (x != tree->nil) {
        y = x;
        if (comp(z->key, x->key) < 0) {
            x = x->left;
        } else if (comp(z->key, x->key) > 0) {
            x = x->right;
        } else {
            free(x->value);
            x->value = strdup(z->value);
            free(z->key);
            free(z->value);
            free(z);
            return;
        }
    }
    z->parent = y;
    if (y == tree->nil) {
        tree->root = z;
    } else if (comp(z->key, y->key) < 0) {
        y->left = z;
    } else {
        y->right = z;
    }
    z->left = tree->nil;
    z->right = tree->nil;
    z->color = RED;
    insertFixup(tree, z);
}

// find minimum node in subtree
RedBlackTreeNode *minimum(RedBlackTree *tree, RedBlackTreeNode *x) {
    while (x->left != tree->nil) {
        x = x->left;
    }
    return x;
}

// transplant a subtree
void transplant(RedBlackTree *tree, RedBlackTreeNode *u, RedBlackTreeNode *v) {
    if (u->parent == tree->nil) {
        tree->root = v;
    } else if (u == u->parent->left) {
        u->parent->left = v;
    } else {
        u->parent->right = v;
    }
    v->parent = u->parent;
}

// fix the tree after deletion
void deleteFixup(RedBlackTree *tree, RedBlackTreeNode *x) {
    while (x != tree->root && x->color == BLACK) {
        if (x == x->parent->left) {
            RedBlackTreeNode *w = x->parent->right;
            if (w->color == RED) {
                w->color = BLACK;
                x->parent->color = RED;
                rotateLeft(tree, x->parent);
                w = x->parent->right;
            }
            if (w->left->color == BLACK && w->right->color == BLACK) {
                w->color = RED;
                x = x->parent;
            } else {
                if (w->right->color == BLACK) {
                    w->left->color = BLACK;
                    w->color = RED;
                    rotateRight(tree, w);
                    w = x->parent->right;
                }
                w->color = x->parent->color;
                x->parent->color = BLACK;
                w->right->color = BLACK;
                rotateLeft(tree, x->parent);
                x = tree->root;
            }
        } else {
            RedBlackTreeNode *w = x->parent->left;
            if (w->color == RED) {
                w->color = BLACK;
                x->parent->color = RED;
                rotateRight(tree, x->parent);
                w = x->parent->left;
            }
            if (w->right->color == BLACK && w->left->color == BLACK) {
                w->color = RED;
                x = x->parent;
            } else {
                if (w->left->color == BLACK) {
                    w->right->color = BLACK;
                    w->color = RED;
                    rotateLeft(tree, w);
                    w = x->parent->left;
                }
                w->color = x->parent->color;
                x->parent->color = BLACK;
                w->left->color = BLACK;
                rotateRight(tree, x->parent);
                x = tree->root;
            }
        }
    }
    x->color = BLACK;
}

// delete a node from the tree
void delete(RedBlackTree *tree, RedBlackTreeNode *z) {
    RedBlackTreeNode *y = z;
    RedBlackTreeNode *x;
    int yOriginalColor = y->color;

    if (z->left == tree->nil) {
        x = z->right;
        transplant(tree, z, z->right);
    } else if (z->right == tree->nil) {
        x = z->left;
        transplant(tree, z, z->left);
    } else {
        y = minimum(tree, z->right);
        yOriginalColor = y->color;
        x = y->right;
        if (y->parent == z) {
            x->parent = y;
        } else {
            transplant(tree, y, y->right);
            y->right = z->right;
            y->right->parent = y;
        }
        transplant(tree, z, y);
        y->left = z->left;
        y->left->parent = y;
        y->color = z->color;
    }

    if (yOriginalColor == BLACK) {
        deleteFixup(tree, x);
    }

    free(z->key);
    free(z->value);
    free(z);
}

// search for a node by key
RedBlackTreeNode *search(RedBlackTree *tree, RedBlackTreeNode *x, char *key) {
    if (x == tree->nil || strcmp(key, x->key) == 0) {
        return x;
    }
    if (strcmp(key, x->key) < 0) {
        return search(tree, x->left, key);
    } else {
        return search(tree, x->right, key);
    }
}

// delete a node by key
void deleteByKey(RedBlackTree *tree, char *key) {
    RedBlackTreeNode *z = search(tree, tree->root, key);
    if (z != tree->nil) {
        delete(tree, z);
    } else {
        printf("Key not found: %s\n", key);
    }
}

void freeNode(RedBlackTree *tree, RedBlackTreeNode *node) {
    if (node == tree->nil) {
        return;
    }
    freeNode(tree, node->left);
    freeNode(tree, node->right);
    free(node->key);
    free(node->value);
    free(node);
}

void freeRedBlackTree(RedBlackTree *tree) {
    if (tree == NULL) {
        return;
    }
    freeNode(tree, tree->root);
    free(tree->nil->key);
    free(tree->nil->value);
    free(tree->nil);
    free(tree);
}


void printTreeHelper(RedBlackTreeNode *root, RedBlackTreeNode *nil, int space) {
    if (root == nil) {
        return;
    }

    // Increase distance between levels
    space += 10;

    // Process right child first (above the parent)
    printTreeHelper(root->right, nil, space);

    // Print current node after space
    printf("\n");
    for (int i = 10; i < space; i++) {
        printf(" ");
    }
    printf("%s (%s)\n", root->key, root->color == RED ? "R" : "B");

    // Process left child (below the parent)
    printTreeHelper(root->left, nil, space);
}

// Wrapper function to print the tree
void printTree(RedBlackTree *tree) {
    printf("\n--------------------");
    printTreeHelper(tree->root, tree->nil, 0);
    printf("--------------------\n");
}

// Test Cases
void testRedBlackTree() {
    RedBlackTree *tree = createRedBlackTree();

    // Test Case 0: Insert nodes
    insert(tree, createNode("Athena", "Wisdom"));
    insert(tree, createNode("Zeus", "Thunder"));
    insert(tree, createNode("Hades", "Underworld"));
    insert(tree, createNode("Poseidon", "Sea"));
    insert(tree, createNode("Hermes", "Messenger"));
    insert(tree, createNode("Demeter", "Harvest"));
    insert(tree, createNode("Dionysus", "Wine"));
    insert(tree, createNode("Ares", "War"));
    insert(tree, createNode("Artemis", "Hunt"));
    insert(tree, createNode("Hephaestus", "Forge"));
    printTree(tree);
    printf("\n");

    // free tree
    freeRedBlackTree(tree);

    // new tree
    tree = createRedBlackTree();

    // Test Case 1: Empty Tree
    printf("Test Case 1: Empty Tree\n");
    printf("Search for 'Athena': %s\n", search(tree, tree->root, "Athena") == tree->nil ? "Not Found" : "Found");
    deleteByKey(tree, "Athena"); // do nothing
    printf("\n");

    // Test Case 2: Single Node Tree
    printf("Test Case 2: Single Node Tree\n");
    insert(tree, createNode("Athena", "Wisdom"));
    printf("Inorder Walk:\n");
    inorderWalk(tree->root, tree->nil);
    printf("Search for 'Athena': %s\n", search(tree, tree->root, "Athena") == tree->nil ? "Not Found" : "Found");
    deleteByKey(tree, "Athena"); // delete the root
    printf("Inorder Walk after deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printf("\n");

    // Test Case 3: Insertion of Duplicate Keys
    printf("Test Case 3: Insertion of Duplicate Keys\n");
    insert(tree, createNode("Athena", "Wisdom"));
    insert(tree, createNode("Athena", "New Value")); // update value or ignore
    printf("Inorder Walk:\n");
    inorderWalk(tree->root, tree->nil);
    printf("\n");

    // Test Case 4: Deletion of Non-Existent Keys
    printf("Test Case 4: Deletion of Non-Existent Keys\n");
    deleteByKey(tree, "NonExistentKey"); // do nothing
    printf("\n");

    // Test Case 5: Deletion of Root Node
    printf("Test Case 5: Deletion of Root Node\n");
    insert(tree, createNode("Athena", "Wisdom"));
    insert(tree, createNode("Zeus", "Thunder"));
    insert(tree, createNode("Hades", "Underworld"));
    printf("Inorder Walk before deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    printf("\n");
    deleteByKey(tree, "Hades"); // delete the root
    printf("Inorder Walk after deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    printf("\n");

    // Test Case 6: Deletion of Leaf Nodes
    printf("Test Case 6: Deletion of Leaf Nodes\n");
    insert(tree, createNode("Poseidon", "Sea"));
    printf("Inorder Walk before deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    printf("\n");
    deleteByKey(tree, "Athena"); // delete the leaf node
    printf("Inorder Walk after deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    printf("\n");

    // Test Case 7: Deletion of Nodes with One Child
    printf("Test Case 7: Deletion of Nodes with One Child\n");
    insert(tree, createNode("Hermes", "Messenger"));
    insert(tree, createNode("Demeter", "Harvest"));
    printf("Inorder Walk before deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    deleteByKey(tree, "Hermes"); // delete node with one child
    printf("Inorder Walk after deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    printf("\n");

    // Test Case 8: Deletion of Nodes with Two Children
    printf("Test Case 8: Deletion of Nodes with Two Children\n");
    insert(tree, createNode("Dionysus", "Wine"));
    insert(tree, createNode("Ares", "War"));
    printf("Inorder Walk before deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    deleteByKey(tree, "Demeter"); // delete node with two children
    printf("Inorder Walk after deletion:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    printf("\n");

    // Test Case 9: Large Tree Stress Test
    printf("Test Case 9: Large Tree Stress Test\n");
    for (int i = 0; i < 100; i++) {
        char key[10], value[10];
        sprintf(key, "Key%d", i);
        sprintf(value, "Value%d", i);
        insert(tree, createNode(key, value));
    }
//  printTree(tree);
    printf("Inorder Walk after insertions:\n");
    inorderWalk(tree->root, tree->nil);
    for (int i = 0; i < 100; i++) {
        char key[10];
        sprintf(key, "Key%d", i);
        deleteByKey(tree, key);
    }
    printTree(tree);
    printf("Inorder Walk after deletions:\n");
    inorderWalk(tree->root, tree->nil);
    printTree(tree);
    printf("\n");
}

int main() {
    testRedBlackTree();
    return 0;
}
