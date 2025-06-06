#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>

typedef struct {
    float feature1;
    float feature2;
    int class;
} DataPoint;

DataPoint dataset[] = {
    {2.0, 3.0, 0},
    {1.5, 2.5, 0},
    {3.0, 4.0, 0},
    {5.0, 2.0, 1},
    {4.5, 3.0, 1},
    {6.0, 2.5, 1}
};

typedef struct Node {
    int is_leaf;
    int class_label;
    int split_feature;
    float split_value;
    struct Node *left;
    struct Node *right;
} Node;

// --- Forward Declarations ---
Node* create_leaf(int class_label);
Node* create_decision_node(int split_feature, float split_value, Node* left, Node* right);
float gini_impurity(DataPoint* data, int n);
void find_best_split(DataPoint* data, int n, int* best_feature, float* best_value);
Node* build_tree(DataPoint* data, int n, int depth);
int predict(Node* tree, float* features);

// --- Function Implementations ---
Node* create_leaf(int class_label) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->is_leaf = 1;
    node->class_label = class_label;
    node->left = NULL;
    node->right = NULL;
    return node;
}

Node* create_decision_node(int split_feature, float split_value, Node* left, Node* right) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->is_leaf = 0;
    node->split_feature = split_feature;
    node->split_value = split_value;
    node->left = left;
    node->right = right;
    return node;
}

float gini_impurity(DataPoint* data, int n) {
    if (n == 0) return 0.0;
    
    int counts[2] = {0, 0};
    for (int i = 0; i < n; i++) {
        counts[data[i].class]++;
    }
    
    float impurity = 1.0;
    for (int i = 0; i < 2; i++) {
        float prob = (float)counts[i] / n;
        impurity -= prob * prob;
    }
    return impurity;
}

void find_best_split(DataPoint* data, int n, int* best_feature, float* best_value) {
    float best_impurity = FLT_MAX;
    
    // Try splitting on feature1
    for (int i = 0; i < n; i++) {
        float split_value = data[i].feature1;
        float left_impurity = gini_impurity(data, i);
        float right_impurity = gini_impurity(data + i, n - i);
        float total_impurity = (i * left_impurity + (n - i) * right_impurity) / n;
        
        if (total_impurity < best_impurity) {
            best_impurity = total_impurity;
            *best_feature = 0;
            *best_value = split_value;
        }
    }
    
    // Try splitting on feature2 (similar logic)
    for (int i = 0; i < n; i++) {
        float split_value = data[i].feature2;
        float left_impurity = gini_impurity(data, i);
        float right_impurity = gini_impurity(data + i, n - i);
        float total_impurity = (i * left_impurity + (n - i) * right_impurity) / n;
        
        if (total_impurity < best_impurity) {
            best_impurity = total_impurity;
            *best_feature = 1;
            *best_value = split_value;
        }
    }
}

Node* build_tree(DataPoint* data, int n, int depth) {
    if (n <= 2 || depth >= 3) {
        int class_counts[2] = {0, 0};
        for (int i = 0; i < n; i++) class_counts[data[i].class]++;
        return create_leaf(class_counts[1] > class_counts[0] ? 1 : 0);
    }
    
    int best_feature;
    float best_value;
    find_best_split(data, n, &best_feature, &best_value);
    
    // Split data into left and right
    int left_count = 0;
    for (int i = 0; i < n; i++) {
        if ((best_feature == 0 && data[i].feature1 <= best_value) ||
            (best_feature == 1 && data[i].feature2 <= best_value)) {
            left_count++;
        }
    }
    
    DataPoint* left_data = (DataPoint*)malloc(left_count * sizeof(DataPoint));
    DataPoint* right_data = (DataPoint*)malloc((n - left_count) * sizeof(DataPoint));
    
    int left_idx = 0, right_idx = 0;
    for (int i = 0; i < n; i++) {
        if ((best_feature == 0 && data[i].feature1 <= best_value) ||
            (best_feature == 1 && data[i].feature2 <= best_value)) {
            left_data[left_idx++] = data[i];
        } else {
            right_data[right_idx++] = data[i];
        }
    }
    
    Node* left = build_tree(left_data, left_count, depth + 1);
    Node* right = build_tree(right_data, n - left_count, depth + 1);
    
    free(left_data);
    free(right_data);
    
    return create_decision_node(best_feature, best_value, left, right);
}

int predict(Node* tree, float* features) {
    while (!tree->is_leaf) {
        if (features[tree->split_feature] <= tree->split_value) {
            tree = tree->left;
        } else {
            tree = tree->right;
        }
    }
    return tree->class_label;
}

// Recursively free the tree
void free_tree(Node* tree) {
    if (tree == NULL) return;
    if (!tree->is_leaf) {
        free_tree(tree->left);
        free_tree(tree->right);
    }
    free(tree);
}

int main() {
    Node* tree = build_tree(dataset, 6, 0);
    
    DataPoint test = {3.5, 3.5, -1};
    float features[] = {test.feature1, test.feature2};
    int prediction = predict(tree, features);
    printf("Prediction: %d\n", prediction);
    
    free_tree(tree); // Clean up memory
    return 0;
}

// This code implements a simple decision tree classifier in C.
// It builds a decision tree based on a small dataset and predicts the class of a new data point.
// The decision tree is built using the Gini impurity criterion for splitting.
// The code includes functions for creating nodes, calculating Gini impurity, finding the best split,
// building the tree, making predictions, and freeing the tree memory.
// The main function demonstrates the usage of the decision tree by building it from a dataset and making a prediction.
// The dataset consists of two features and binary class labels.
// The decision tree is built recursively, and the prediction is made by traversing the tree based on feature values.
// The code is structured to be clear and modular, with separate functions for each task.
// The decision tree is limited to a maximum depth of 3 for simplicity, and it can handle up to 2 classes.
