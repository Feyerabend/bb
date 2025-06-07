#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <string.h>

#define MAX_CLASSES 10
#define MAX_FEATURES 10
#define MIN_SAMPLES_SPLIT 2
#define MAX_DEPTH 10

typedef struct {
    float features[MAX_FEATURES];
    int class;
} DataPoint;

typedef struct Node {
    int is_leaf;
    int class_label;
    float class_probabilities[MAX_CLASSES];
    int split_feature;
    float split_value;
    int samples_count;
    float impurity;
    struct Node *left;
    struct Node *right;
} Node;

typedef struct {
    int num_features;
    int num_classes;
    int max_depth;
    int min_samples_split;
    float min_impurity_decrease;
} TreeConfig;

typedef struct {
    int feature;
    float value;
    float impurity_decrease;
    int left_count;
    int right_count;
} SplitResult;

// Enhanced dataset with more variety
DataPoint dataset[] = {
    {{2.0, 3.0, 1.5}, 0},
    {{1.5, 2.5, 2.0}, 0},
    {{3.0, 4.0, 1.8}, 0},
    {{2.2, 3.5, 1.6}, 0},
    {{5.0, 2.0, 3.2}, 1},
    {{4.5, 3.0, 2.8}, 1},
    {{6.0, 2.5, 3.5}, 1},
    {{5.5, 1.8, 3.0}, 1},
    {{7.0, 4.0, 4.2}, 2},
    {{6.5, 3.8, 4.0}, 2},
    {{8.0, 4.5, 4.5}, 2}
};

// --- Enhanced Function Declarations ---
Node* create_leaf(int* class_counts, int total_samples, int num_classes);
Node* create_decision_node(int split_feature, float split_value, Node* left, Node* right);
float calculate_gini_impurity(int* class_counts, int total_samples, int num_classes);
float calculate_entropy(int* class_counts, int total_samples, int num_classes);
void count_classes(DataPoint* data, int n, int* class_counts, int num_classes);
int find_majority_class(int* class_counts, int num_classes);
SplitResult find_best_split(DataPoint* data, int n, TreeConfig* config);
Node* build_tree_recursive(DataPoint* data, int n, int depth, TreeConfig* config);
int predict_class(Node* tree, float* features);
float* predict_probabilities(Node* tree, float* features);
void print_tree(Node* tree, int depth, TreeConfig* config);
void free_tree(Node* tree);
double evaluate_accuracy(Node* tree, DataPoint* test_data, int test_size);

// --- Enhanced Function Implementations ---

Node* create_leaf(int* class_counts, int total_samples, int num_classes) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->is_leaf = 1;
    node->class_label = find_majority_class(class_counts, num_classes);
    node->samples_count = total_samples;
    node->impurity = calculate_gini_impurity(class_counts, total_samples, num_classes);
    node->left = NULL;
    node->right = NULL;
    
    // Calculate class probabilities
    for (int i = 0; i < num_classes; i++) {
        node->class_probabilities[i] = (float)class_counts[i] / total_samples;
    }
    
    return node;
}

Node* create_decision_node(int split_feature, float split_value, Node* left, Node* right) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->is_leaf = 0;
    node->split_feature = split_feature;
    node->split_value = split_value;
    node->left = left;
    node->right = right;
    node->samples_count = left->samples_count + right->samples_count;
    return node;
}

float calculate_gini_impurity(int* class_counts, int total_samples, int num_classes) {
    if (total_samples == 0) return 0.0;
    
    float impurity = 1.0;
    for (int i = 0; i < num_classes; i++) {
        float prob = (float)class_counts[i] / total_samples;
        impurity -= prob * prob;
    }
    return impurity;
}

float calculate_entropy(int* class_counts, int total_samples, int num_classes) {
    if (total_samples == 0) return 0.0;
    
    float entropy = 0.0;
    for (int i = 0; i < num_classes; i++) {
        if (class_counts[i] > 0) {
            float prob = (float)class_counts[i] / total_samples;
            entropy -= prob * log2(prob);
        }
    }
    return entropy;
}

void count_classes(DataPoint* data, int n, int* class_counts, int num_classes) {
    memset(class_counts, 0, num_classes * sizeof(int));
    for (int i = 0; i < n; i++) {
        if (data[i].class < num_classes) {
            class_counts[data[i].class]++;
        }
    }
}

int find_majority_class(int* class_counts, int num_classes) {
    int max_count = 0;
    int majority_class = 0;
    
    for (int i = 0; i < num_classes; i++) {
        if (class_counts[i] > max_count) {
            max_count = class_counts[i];
            majority_class = i;
        }
    }
    return majority_class;
}

SplitResult find_best_split(DataPoint* data, int n, TreeConfig* config) {
    SplitResult best_split = {-1, 0.0, -FLT_MAX, 0, 0};
    
    int parent_counts[MAX_CLASSES];
    count_classes(data, n, parent_counts, config->num_classes);
    float parent_impurity = calculate_gini_impurity(parent_counts, n, config->num_classes);
    
    // Try each feature
    for (int feature = 0; feature < config->num_features; feature++) {
        // Sort data by current feature (simplified approach)
        for (int threshold_idx = 0; threshold_idx < n; threshold_idx++) {
            float threshold = data[threshold_idx].features[feature];
            
            // Count samples in left and right splits
            int left_counts[MAX_CLASSES] = {0};
            int right_counts[MAX_CLASSES] = {0};
            int left_total = 0, right_total = 0;
            
            for (int i = 0; i < n; i++) {
                if (data[i].features[feature] <= threshold) {
                    left_counts[data[i].class]++;
                    left_total++;
                } else {
                    right_counts[data[i].class]++;
                    right_total++;
                }
            }
            
            // Skip if split doesn't separate data
            if (left_total == 0 || right_total == 0) continue;
            
            // Calculate weighted impurity
            float left_impurity = calculate_gini_impurity(left_counts, left_total, config->num_classes);
            float right_impurity = calculate_gini_impurity(right_counts, right_total, config->num_classes);
            float weighted_impurity = (left_total * left_impurity + right_total * right_impurity) / n;
            
            float impurity_decrease = parent_impurity - weighted_impurity;
            
            if (impurity_decrease > best_split.impurity_decrease) {
                best_split.feature = feature;
                best_split.value = threshold;
                best_split.impurity_decrease = impurity_decrease;
                best_split.left_count = left_total;
                best_split.right_count = right_total;
            }
        }
    }
    
    return best_split;
}

Node* build_tree_recursive(DataPoint* data, int n, int depth, TreeConfig* config) {
    int class_counts[MAX_CLASSES];
    count_classes(data, n, class_counts, config->num_classes);
    
    // Check stopping criteria
    if (n < config->min_samples_split || 
        depth >= config->max_depth ||
        calculate_gini_impurity(class_counts, n, config->num_classes) == 0.0) {
        return create_leaf(class_counts, n, config->num_classes);
    }
    
    // Find best split
    SplitResult split = find_best_split(data, n, config);
    
    // If no good split found or minimum impurity decrease not met
    if (split.feature == -1 || split.impurity_decrease < config->min_impurity_decrease) {
        return create_leaf(class_counts, n, config->num_classes);
    }
    
    // Split data
    DataPoint* left_data = (DataPoint*)malloc(split.left_count * sizeof(DataPoint));
    DataPoint* right_data = (DataPoint*)malloc(split.right_count * sizeof(DataPoint));
    
    int left_idx = 0, right_idx = 0;
    for (int i = 0; i < n; i++) {
        if (data[i].features[split.feature] <= split.value) {
            left_data[left_idx++] = data[i];
        } else {
            right_data[right_idx++] = data[i];
        }
    }
    
    // Recursively build subtrees
    Node* left = build_tree_recursive(left_data, split.left_count, depth + 1, config);
    Node* right = build_tree_recursive(right_data, split.right_count, depth + 1, config);
    
    free(left_data);
    free(right_data);
    
    return create_decision_node(split.feature, split.value, left, right);
}

int predict_class(Node* tree, float* features) {
    while (!tree->is_leaf) {
        if (features[tree->split_feature] <= tree->split_value) {
            tree = tree->left;
        } else {
            tree = tree->right;
        }
    }
    return tree->class_label;
}

float* predict_probabilities(Node* tree, float* features) {
    while (!tree->is_leaf) {
        if (features[tree->split_feature] <= tree->split_value) {
            tree = tree->left;
        } else {
            tree = tree->right;
        }
    }
    return tree->class_probabilities;
}

void print_tree(Node* tree, int depth, TreeConfig* config) {
    if (tree == NULL) return;
    
    for (int i = 0; i < depth; i++) printf("  ");
    
    if (tree->is_leaf) {
        printf("Leaf: class=%d, samples=%d, impurity=%.3f\n", 
               tree->class_label, tree->samples_count, tree->impurity);
    } else {
        printf("Split: feature_%d <= %.2f, samples=%d\n", 
               tree->split_feature, tree->split_value, tree->samples_count);
        print_tree(tree->left, depth + 1, config);
        print_tree(tree->right, depth + 1, config);
    }
}

double evaluate_accuracy(Node* tree, DataPoint* test_data, int test_size) {
    int correct = 0;
    for (int i = 0; i < test_size; i++) {
        int prediction = predict_class(tree, test_data[i].features);
        if (prediction == test_data[i].class) {
            correct++;
        }
    }
    return (double)correct / test_size;
}

void free_tree(Node* tree) {
    if (tree == NULL) return;
    if (!tree->is_leaf) {
        free_tree(tree->left);
        free_tree(tree->right);
    }
    free(tree);
}

int main() {
    printf("Enhanced Decision Tree Classifier\n");
    printf("=================================\n\n");
    
    // Configure the decision tree
    TreeConfig config = {
        .num_features = 3,
        .num_classes = 3,
        .max_depth = 5,
        .min_samples_split = 2,
        .min_impurity_decrease = 0.0
    };
    
    int dataset_size = sizeof(dataset) / sizeof(dataset[0]);
    
    // Build the decision tree
    printf("Building decision tree...\n");
    Node* tree = build_tree_recursive(dataset, dataset_size, 0, &config);
    
    // Print the tree structure
    printf("\nDecision Tree Structure:\n");
    print_tree(tree, 0, &config);
    
    // Test predictions
    printf("\nTesting predictions:\n");
    DataPoint test_cases[] = {
        {{3.5, 3.5, 2.0}, -1},  // Unknown class for testing
        {{1.0, 2.0, 1.0}, -1},
        {{7.5, 4.2, 4.8}, -1}
    };
    
    for (int i = 0; i < 3; i++) {
        int prediction = predict_class(tree, test_cases[i].features);
        float* probabilities = predict_probabilities(tree, test_cases[i].features);
        
        printf("Test case %d: [%.1f, %.1f, %.1f] -> Class %d\n", 
               i+1, test_cases[i].features[0], test_cases[i].features[1], 
               test_cases[i].features[2], prediction);
        
        printf("  Class probabilities: ");
        for (int j = 0; j < config.num_classes; j++) {
            printf("Class %d: %.3f ", j, probabilities[j]);
        }
        printf("\n");
    }
    
    // Evaluate on training data (for demonstration)
    double accuracy = evaluate_accuracy(tree, dataset, dataset_size);
    printf("\nTraining accuracy: %.2f%%\n", accuracy * 100);
    
    // Clean up
    free_tree(tree);
    
    return 0;
}

/*
 * Decision Tree Implementation Features:
 * 
 * 1. Multi-class support (up to MAX_CLASSES)
 * 2. Multi-feature support (up to MAX_FEATURES)
 * 3. Configurable tree parameters (depth, minimum samples, etc.)
 * 4. Both Gini impurity and entropy calculations
 * 5. Class probability predictions
 * 6. Tree visualization
 * 7. Accuracy evaluation
 * 8. Better memory management
 * 9. More robust split finding algorithm
 * 10. Stopping criteria to prevent overfitting
 */