#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node* next;
    struct Node* prev;
} Node;

Node* createNode(int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (!newNode) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    newNode->value = value;
    newNode->next = NULL;
    newNode->prev = NULL;
    return newNode;
}

void insert(Node** head, int value) {
    Node* newNode = createNode(value);
    if (*head == NULL) {
        *head = newNode;
        return;
    }
    Node* current = *head;
    while (current->next != NULL) {
        current = current->next;
    }
    current->next = newNode;
    newNode->prev = current;
}

void delete(Node** head, int value) {
    if (*head == NULL) return;

    Node* current = *head;
    while (current && current->value != value) {
        current = current->next;
    }

    if (current == NULL) return;  // value not found

    if (current->prev) {
        current->prev->next = current->next;
    } else {
        *head = current->next;  // deleting head
    }

    if (current->next) {
        current->next->prev = current->prev;
    }

    free(current);
}

int search(Node* head, int value) {
    Node* current = head;
    while (current != NULL) {
        if (current->value == value) {
            return 1;  // found
        }
        current = current->next;
    }
    return 0;  // not found
}


void printForward(Node* head) {
    Node* current = head;
    while (current != NULL) {
        printf("%d <-> ", current->value);
        current = current->next;
    }
    printf("NULL\n");
}

void printBackward(Node* head) {
    if (head == NULL) return;

    Node* current = head;
    while (current->next != NULL) {
        current = current->next;  // move to last node
    }

    while (current != NULL) {
        printf("%d <-> ", current->value);
        current = current->prev;
    }
    printf("NULL\n");
}

void freeList(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
}

// example
int main() {
    Node* head = NULL;

    insert(&head, 1);
    insert(&head, 2);
    insert(&head, 3);

    printForward(head);   // Output: 1 <-> 2 <-> 3 <-> NULL
    printBackward(head);  // Output: 3 <-> 2 <-> 1 <-> NULL

    delete(&head, 2);
    
    printForward(head);   // Output: 1 <-> 3 <-> NULL

    printf("Search 3: %s\n", search(head, 3) ? "Found" : "Not Found"); // Output: Found
    printf("Search 5: %s\n", search(head, 5) ? "Found" : "Not Found"); // Output: Not Found

    freeList(head);
    return 0;
}
