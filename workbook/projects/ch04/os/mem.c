#define HEAP_SIZE 4096
static uint8_t heap[HEAP_SIZE];

typedef struct BlockHeader {
    uint32_t size;            // size of the block (excluding header)
    uint8_t in_use;           // 1 in use, 0 is free
    struct BlockHeader *next; // pointer to the next block in the linked list
} BlockHeader;

#define HEADER_SIZE sizeof(BlockHeader)

BlockHeader *free_list = (BlockHeader *) heap;

void memory_init() {
    free_list->size = HEAP_SIZE - HEADER_SIZE;
    free_list->in_use = 0;
    free_list->next = NULL;
}

void *malloc(uint32_t size) {
    BlockHeader *current = free_list;

    while (current) {
        if (!current->in_use && current->size >= size) {
            // found a suitable block, split if necessary
            if (current->size > size + HEADER_SIZE) {
                // create a new block header for the remaining free space
                BlockHeader *new_block = (BlockHeader *)((uint8_t *)current + HEADER_SIZE + size);
                new_block->size = current->size - size - HEADER_SIZE;
                new_block->in_use = 0;
                new_block->next = current->next;

                // update current block
                current->size = size;
                current->next = new_block;
            }
            current->in_use = 1;
            return (void *)((uint8_t *)current + HEADER_SIZE); // return pointer after header
        }
        current = current->next;
    }
    return NULL; // no suitable block found
}

void free(void *ptr) {
    if (!ptr) return;

    BlockHeader *block = (BlockHeader *)((uint8_t *)ptr - HEADER_SIZE);
    block->in_use = 0;

    // coalesce with next block if free
    if (block->next && !block->next->in_use) {
        block->size += HEADER_SIZE + block->next->size;
        block->next = block->next->next;
    }

    // coalesce with previous block if free
    BlockHeader *prev = free_list;
    while (prev && prev->next != block) {
        prev = prev->next;
    }

    if (prev && !prev->in_use) {
        prev->size += HEADER_SIZE + block->size;
        prev->next = block->next;
    }
}

void test_memory_manager() {
    memory_init();
    
    void *ptr1 = malloc(100);
    uart_send_string("Allocated 100 bytes\n");

    void *ptr2 = malloc(200);
    uart_send_string("Allocated 200 bytes\n");

    free(ptr1);
    uart_send_string("Freed 100 bytes\n");

    void *ptr3 = malloc(50);
    uart_send_string("Allocated 50 bytes\n");

    free(ptr2);
    uart_send_string("Freed 200 bytes\n");

    free(ptr3);
    uart_send_string("Freed 50 bytes\n");
}
