#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct Node {
    int key, degree;
    struct Node *parent, *child, *next, *prev;
    int mark;
} Node;

typedef struct FibonacciHeap {
    Node *min;
    int total_nodes;
} FibonacciHeap;

Node* create_node(int key) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->key = key;
    node->degree = 0;
    node->parent = node->child = NULL;
    node->mark = 0;
    node->next = node->prev = node;
    return node;
}

FibonacciHeap* create_heap() {
    FibonacciHeap* heap = (FibonacciHeap*)malloc(sizeof(FibonacciHeap));
    heap->min = NULL;
    heap->total_nodes = 0;
    return heap;
}

Node* merge_lists(Node* a, Node* b) {
    if (!a) return b;
    if (!b) return a;
    Node* temp = a->next;
    a->next = b->next;
    b->next->prev = a;
    b->next = temp;
    temp->prev = b;
    return (a->key < b->key) ? a : b;
}

void insert(FibonacciHeap* heap, int key) {
    Node* node = create_node(key);
    heap->min = merge_lists(heap->min, node);
    heap->total_nodes++;
}

void remove_from_list(Node* node) {
    if (node->next == node) return;
    node->prev->next = node->next;
    node->next->prev = node->prev;
}

void link(Node* child, Node* parent) {
    remove_from_list(child);
    child->next = child->prev = child;
    parent->child = merge_lists(parent->child, child);
    child->parent = parent;
    parent->degree++;
    child->mark = 0;
}

void consolidate(FibonacciHeap* heap) {
    int max_degree = (int)(log(heap->total_nodes) / log(2)) + 1;
    Node* degree_table[max_degree];
    for (int i = 0; i < max_degree; i++) degree_table[i] = NULL;
    
    Node* start = heap->min;
    Node* node = start;
    do {
        Node* x = node;
        node = node->next;
        int d = x->degree;
        while (degree_table[d]) {
            Node* y = degree_table[d];
            if (x->key > y->key) {
                Node* temp = x;
                x = y;
                y = temp;
            }
            link(y, x);
            degree_table[d] = NULL;
            d++;
        }
        degree_table[d] = x;
    } while (node != start);
    
    heap->min = NULL;
    for (int i = 0; i < max_degree; i++) {
        if (degree_table[i]) {
            heap->min = merge_lists(heap->min, degree_table[i]);
        }
    }
}

Node* extract_min(FibonacciHeap* heap) {
    Node* min_node = heap->min;
    if (min_node) {
        if (min_node->child) {
            Node* child = min_node->child;
            do {
                child->parent = NULL;
                child = child->next;
            } while (child != min_node->child);
            heap->min = merge_lists(heap->min, min_node->child);
        }
        remove_from_list(min_node);
        if (min_node == min_node->next) {
            heap->min = NULL;
        } else {
            heap->min = min_node->next;
            consolidate(heap);
        }
        heap->total_nodes--;
    }
    return min_node;
}


int main() {
    FibonacciHeap* heap = create_heap();
    insert(heap, 10);
    insert(heap, 3);
    insert(heap, 7);
    printf("Extracted min: %d\n", extract_min(heap)->key);  // Output: 3
    return 0;
}
