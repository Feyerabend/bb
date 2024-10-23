#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// allocator

#define MEMORY_POOL_SIZE 1024
uint8_t memory_pool[MEMORY_POOL_SIZE];

typedef struct BlockHeader {
    size_t size;
    int is_free;
    struct BlockHeader* next;
} BlockHeader;

BlockHeader* free_list = NULL;

void memory_init() {
    free_list = (BlockHeader*)memory_pool;
    free_list->size = MEMORY_POOL_SIZE - sizeof(BlockHeader);
    free_list->is_free = 1;
    free_list->next = NULL;
}

// merging adjacent free blocks
void merge_free_blocks() {
    BlockHeader* current = (BlockHeader*)memory_pool;
    while (current != NULL && current->next != NULL) {
        BlockHeader* next_block = current->next;
        if (current->is_free && next_block->is_free) {
            current->size += sizeof(BlockHeader) + next_block->size;
            current->next = next_block->next;
        } else {
            current = next_block;
        }
    }
}

// allocator (malloc equivalent)
void* mem_malloc(size_t size) {
    BlockHeader* current = free_list;
    while (current != NULL) {
        if (current->is_free && current->size >= size) {
            current->is_free = 0;
            return (void*)((uint8_t*)current + sizeof(BlockHeader));
        }
        current = current->next;
    }
    return NULL;
}

void mem_free(void* ptr) {
    if (ptr == NULL)
        return;
    BlockHeader* block = (BlockHeader*)((uint8_t*)ptr - sizeof(BlockHeader));
    block->is_free = 1;
    merge_free_blocks();
}

// alloc memory for existing block (realloc equivalent)
void* mem_realloc(void* ptr, size_t new_size) {
    if (ptr == NULL)
        return mem_malloc(new_size);
    
    BlockHeader* old_block = (BlockHeader*)((uint8_t*)ptr - sizeof(BlockHeader));
    if (old_block->size >= new_size)
        return ptr;  // if the block is already large enough

    void* new_ptr = mem_malloc(new_size);
    if (new_ptr != NULL) {
        memcpy(new_ptr, ptr, old_block->size);
        mem_free(ptr);
    }
    return new_ptr;
}

// vm

typedef struct VM {
    void* allocated_blocks[10];
    int block_count;
} VM;

void vm_init(VM* vm) {
    vm->block_count = 0;
}

void* vm_alloc(VM* vm, size_t size) {
    void* addr = mem_malloc(size);
    if (addr != NULL) {
        vm->allocated_blocks[vm->block_count++] = addr;
        printf("Allocated %zu bytes at address %p\n", size, addr);
    }
    return addr;
}

void vm_free(VM* vm, void* addr) {
    mem_free(addr);
    printf("Freed memory at address %p\n", addr);
}

void* vm_realloc(VM* vm, void* addr, size_t new_size) {
    void* new_addr = mem_realloc(addr, new_size);
    if (new_addr != NULL) {
        printf("Reallocated memory from %p to %p, new size: %zu bytes\n", addr, new_addr, new_size);
    }
    return new_addr;
}

void vm_store(void* addr, int offset, int value) {
    int* block = (int*)((uint8_t*)addr + offset);
    *block = value;
    printf("Stored value %d at offset %d\n", value, offset);
}

int vm_load(void* addr, int offset) {
    int* block = (int*)((uint8_t*)addr + offset);
    int value = *block;
    printf("Loaded value %d from offset %d\n", value, offset);
    return value;
}

// sample

int main() {
    memory_init();
    VM vm;
    vm_init(&vm);
    const int z = sizeof(int);

    // 1: allocate small block for 3 integers
    void* block = vm_alloc(&vm, 3 * z);

    // 2: store values in block (simulating "dynamic array")
    vm_store(block, 0 * z, 10);
    vm_store(block, 1 * z, 20);
    vm_store(block, 2 * z, 30);

    // 3: expand block (add more numbers, i.e. reallocating)
    block = vm_realloc(&vm, block, 6 * z);

    // 4: add more values in expanded block
    vm_store(block, 3 * z, 40);
    vm_store(block, 4 * z, 50);
    vm_store(block, 5 * z, 60);

    // 5: retrieve values (from "dynamic array")
    for (int i = 0; i < 6; i++) {
        vm_load(block, i * z);
    }
    // 6: replace value at offset (where 50 lives)
    vm_store(block, 4 * z, 90);

    // 7: retrieve values
    for (int i = 0; i < 6; i++) {
        vm_load(block, i * z);
    }

    // 8: free block
    vm_free(&vm, block);

    return 0;
}
