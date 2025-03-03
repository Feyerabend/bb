#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>


typedef struct Node {
    int value;
    struct Node* next;
} Node;


typedef struct Queue {
    Node* front;
    Node* rear;
    int size;
} Queue;


Queue* createQueue() {
    Queue* q = (Queue*)malloc(sizeof(Queue));
    if (!q) {
        perror("Failed to allocate memory for queue");
        exit(EXIT_FAILURE);
    }
    q->front = q->rear = NULL;
    q->size = 0;
    return q;
}


void enqueue(Queue* q, int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (!newNode) {
        perror("Failed to allocate memory for node");
        exit(EXIT_FAILURE);
    }
    newNode->value = value;
    newNode->next = NULL;

    if (q->rear == NULL) {
        q->front = q->rear = newNode;
    } else {
        q->rear->next = newNode;
        q->rear = newNode;
    }
    q->size++;
}


int dequeue(Queue* q) {
    if (q->front == NULL) {
        fprintf(stderr, "Queue underflow: cannot dequeue from an empty queue.\n");
        exit(EXIT_FAILURE);
    }
    Node* temp = q->front;
    int removedValue = temp->value;

    q->front = q->front->next;
    if (q->front == NULL) {
        q->rear = NULL; // queue is empty
    }

    free(temp);
    q->size--;
    return removedValue;
}


int peek(Queue* q) {
    if (q->front == NULL) {
        fprintf(stderr, "Queue is empty: cannot peek.\n");
        exit(EXIT_FAILURE);
    }
    return q->front->value;
}


bool isEmpty(Queue* q) {
    return q->front == NULL;
}


int size(Queue* q) {
    return q->size;
}


void printQueue(Queue* q) {
    Node* current = q->front;
    printf("Queue: ");
    while (current) {
        printf("%d -> ", current->value);
        current = current->next;
    }
    printf("NULL\n");
}


void freeQueue(Queue* q) {
    Node* current = q->front;
    while (current) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
    free(q);
}

// example
int main() {
    Queue* q = createQueue();
    
    enqueue(q, 10);
    enqueue(q, 20);
    enqueue(q, 30);

    printQueue(q); // Output: Queue: 10 -> 20 -> 30 -> NULL
    
    printf("Dequeued: %d\n", dequeue(q)); // Output: 10
    printf("Front element: %d\n", peek(q)); // Output: 20
    printf("Queue size: %d\n", size(q)); // Output: 2

    printQueue(q); // Output: Queue: 20 -> 30 -> NULL

    freeQueue(q); // Clean up memory

    return 0;
}
