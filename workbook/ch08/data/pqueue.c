#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int priority;
    int value;
} PQNode;

typedef struct {
    PQNode *heap;
    int size;
    int capacity;
    int isMinHeap;  // 1 for Min-Heap, 0 for Max-Heap
} PriorityQueue;

PriorityQueue* createPQ(int capacity, int isMinHeap);
void insertPQ(PriorityQueue *pq, int priority, int value);
int extractPQ(PriorityQueue *pq);
void heapifyUp(PriorityQueue *pq, int index);
void heapifyDown(PriorityQueue *pq, int index);
void swap(PQNode *a, PQNode *b);
void printPQ(PriorityQueue *pq);
void freePQ(PriorityQueue *pq);

PriorityQueue* createPQ(int capacity, int isMinHeap) {
    PriorityQueue *pq = (PriorityQueue *)malloc(sizeof(PriorityQueue));
    pq->heap = (PQNode *)malloc(capacity * sizeof(PQNode));
    pq->size = 0;
    pq->capacity = capacity;
    pq->isMinHeap = isMinHeap;
    return pq;
}

void insertPQ(PriorityQueue *pq, int priority, int value) {
    if (pq->size == pq->capacity) {
        printf("Priority Queue is full\n");
        return;
    }
    PQNode node;
    node.priority = priority;
    node.value = value;

    pq->heap[pq->size] = node;
    heapifyUp(pq, pq->size);
    pq->size++;
}

int extractPQ(PriorityQueue *pq) {
    if (pq->size == 0) {
        printf("Priority Queue is empty\n");
        return -1;
    }
    
    int highestPriorityValue = pq->heap[0].value;  // get value
    pq->heap[0] = pq->heap[pq->size - 1];  // last element -> root
    pq->size--;
    heapifyDown(pq, 0);

    return highestPriorityValue;
}

// .. restore heap after insertion
void heapifyUp(PriorityQueue *pq, int index) {
    int parent = (index - 1) / 2;

    if (index > 0) {
        int condition = pq->isMinHeap
                        ? pq->heap[index].priority < pq->heap[parent].priority
                        : pq->heap[index].priority > pq->heap[parent].priority;

        if (condition) {
            swap(&pq->heap[index], &pq->heap[parent]);
            heapifyUp(pq, parent);
        }
    }
}

// .. restore heap after extraction
void heapifyDown(PriorityQueue *pq, int index) {
    int left = 2 * index + 1;
    int right = 2 * index + 2;
    int selected = index;

    if (pq->isMinHeap) {
        if (left < pq->size && pq->heap[left].priority < pq->heap[selected].priority)
            selected = left;
        if (right < pq->size && pq->heap[right].priority < pq->heap[selected].priority)
            selected = right;
    } else {
        if (left < pq->size && pq->heap[left].priority > pq->heap[selected].priority)
            selected = left;
        if (right < pq->size && pq->heap[right].priority > pq->heap[selected].priority)
            selected = right;
    }

    if (selected != index) {
        swap(&pq->heap[index], &pq->heap[selected]);
        heapifyDown(pq, selected);
    }
}

void swap(PQNode *a, PQNode *b) {
    PQNode temp = *a;
    *a = *b;
    *b = temp;
}


void printPQ(PriorityQueue *pq) {
    for (int i = 0; i < pq->size; i++)
        printf("(%d, %d) ", pq->heap[i].priority, pq->heap[i].value);
    printf("\n");
}


void freePQ(PriorityQueue *pq) {
    free(pq->heap);
    free(pq);
}


int main() {
    printf("Min-Priority Queue (lower number = higher priority):\n");
    PriorityQueue *minPQ = createPQ(10, 1);  // Min-Heap Priority Queue

    insertPQ(minPQ, 3, 100);
    insertPQ(minPQ, 1, 200);
    insertPQ(minPQ, 2, 300);

    printf("Queue: ");
    printPQ(minPQ);  // Output: [(1, 200), (3, 100), (2, 300)]
    
    printf("Extracted: %d\n", extractPQ(minPQ));  // Output: 200 (priority 1)
    printf("Queue after extraction: ");
    printPQ(minPQ);  // Output: [(2, 300), (3, 100)]
    
    printf("\nMax-Priority Queue (higher number = higher priority):\n");
    PriorityQueue *maxPQ = createPQ(10, 0);  // Max-Heap Priority Queue

    insertPQ(maxPQ, 3, 100);
    insertPQ(maxPQ, 1, 200);
    insertPQ(maxPQ, 2, 300);

    printf("Queue: ");
    printPQ(maxPQ);  // Output: [(3, 100), (1, 200), (2, 300)]
    
    printf("Extracted: %d\n", extractPQ(maxPQ));  // Output: 100 (priority 3)
    printf("Queue after extraction: ");
    printPQ(maxPQ);  // Output: [(2, 300), (1, 200)]

    freePQ(minPQ);
    freePQ(maxPQ);

    return 0;
}
