#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *heap;
    int size;
    int capacity;
} Heap;

Heap* createHeap(int capacity);
void insertMinHeap(Heap *h, int value);
void insertMaxHeap(Heap *h, int value);
int extractMin(Heap *h);
int extractMax(Heap *h);
void heapifyUpMin(Heap *h, int index);
void heapifyUpMax(Heap *h, int index);
void heapifyDownMin(Heap *h, int index);
void heapifyDownMax(Heap *h, int index);
void swap(int *a, int *b);
void printHeap(Heap *h);
void freeHeap(Heap *h);

Heap* createHeap(int capacity) {
    Heap *h = (Heap *)malloc(sizeof(Heap));
    h->heap = (int *)malloc(capacity * sizeof(int));
    h->size = 0;
    h->capacity = capacity;
    return h;
}

void insertMinHeap(Heap *h, int value) {
    if (h->size == h->capacity) {
        printf("Heap is full\n");
        return;
    }
    h->heap[h->size] = value;
    heapifyUpMin(h, h->size);
    h->size++;
}

void insertMaxHeap(Heap *h, int value) {
    if (h->size == h->capacity) {
        printf("Heap is full\n");
        return;
    }
    h->heap[h->size] = value;
    heapifyUpMax(h, h->size);
    h->size++;
}

int extractMin(Heap *h) {
    if (h->size == 0) {
        printf("Heap is empty\n");
        return -1;
    }
    int root = h->heap[0];
    h->heap[0] = h->heap[h->size - 1];
    h->size--;
    heapifyDownMin(h, 0);
    return root;
}

int extractMax(Heap *h) {
    if (h->size == 0) {
        printf("Heap is empty\n");
        return -1;
    }
    int root = h->heap[0];
    h->heap[0] = h->heap[h->size - 1];
    h->size--;
    heapifyDownMax(h, 0);
    return root;
}

void heapifyUpMin(Heap *h, int index) {
    int parent = (index - 1) / 2;
    if (index > 0 && h->heap[index] < h->heap[parent]) {
        swap(&h->heap[index], &h->heap[parent]);
        heapifyUpMin(h, parent);
    }
}

void heapifyUpMax(Heap *h, int index) {
    int parent = (index - 1) / 2;
    if (index > 0 && h->heap[index] > h->heap[parent]) {
        swap(&h->heap[index], &h->heap[parent]);
        heapifyUpMax(h, parent);
    }
}

void heapifyDownMin(Heap *h, int index) {
    int left = 2 * index + 1;
    int right = 2 * index + 2;
    int smallest = index;

    if (left < h->size && h->heap[left] < h->heap[smallest])
        smallest = left;
    if (right < h->size && h->heap[right] < h->heap[smallest])
        smallest = right;

    if (smallest != index) {
        swap(&h->heap[index], &h->heap[smallest]);
        heapifyDownMin(h, smallest);
    }
}

void heapifyDownMax(Heap *h, int index) {
    int left = 2 * index + 1;
    int right = 2 * index + 2;
    int largest = index;

    if (left < h->size && h->heap[left] > h->heap[largest])
        largest = left;
    if (right < h->size && h->heap[right] > h->heap[largest])
        largest = right;

    if (largest != index) {
        swap(&h->heap[index], &h->heap[largest]);
        heapifyDownMax(h, largest);
    }
}

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void printHeap(Heap *h) {
    for (int i = 0; i < h->size; i++)
        printf("%d ", h->heap[i]);
    printf("\n");
}

void freeHeap(Heap *h) {
    free(h->heap);
    free(h);
}

int main() {
    Heap *minHeap = createHeap(10);
    Heap *maxHeap = createHeap(10);

    printf("Min-Heap operations:\n");
    insertMinHeap(minHeap, 5);
    insertMinHeap(minHeap, 3);
    insertMinHeap(minHeap, 8);
    insertMinHeap(minHeap, 2);
    
    printf("Min-Heap: ");
    printHeap(minHeap);

    printf("Extracted Min: %d\n", extractMin(minHeap));
    printf("Min-Heap after extraction: ");
    printHeap(minHeap);

    printf("\nMax-Heap operations:\n");
    insertMaxHeap(maxHeap, 5);
    insertMaxHeap(maxHeap, 3);
    insertMaxHeap(maxHeap, 8);
    insertMaxHeap(maxHeap, 2);

    printf("Max-Heap: ");
    printHeap(maxHeap);

    printf("Extracted Max: %d\n", extractMax(maxHeap));
    printf("Max-Heap after extraction: ");
    printHeap(maxHeap);

    freeHeap(minHeap);
    freeHeap(maxHeap);

    return 0;
}
