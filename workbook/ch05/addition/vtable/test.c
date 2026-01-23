#include <stdio.h>
#include <stdlib.h>

// ============================================
// BASE OBJECT
// ============================================

typedef struct Object {
    struct ObjectVTable* vtable;  // ← VTABLE POINTER!
} Object;

typedef struct ObjectVTable {
    void (*destroy)(Object* self);
} ObjectVTable;

void object_destroy(Object* self) {
    free(self);
}

ObjectVTable object_vtable = {
    .destroy = object_destroy
};

// ============================================
// Dog CLASS
// ============================================

typedef struct Dog {
    Object base;  // ← Inheritance via composition
} Dog;

// Dog VTABLE STRUCTURE
typedef struct DogVTable {
    ObjectVTable base;  // ← Inherit base vtable
    void (*bark)(Object* self);  // ← Method pointer
} DogVTable;

// METHOD IMPLEMENTATIONS
void Dog_bark(Object* self) {
    printf("Woof!\n");
}

// VTABLE INSTANCE (GLOBAL)
// This is THE vtable - only ONE exists per class!
DogVTable dog_vtable = {
    .base = { .destroy = object_destroy },
    .bark = Dog_bark,  // ← Points to implementation
};

// CONSTRUCTOR
Dog* Dog_create() {
    Dog* self = malloc(sizeof(Dog));
    self->base.vtable = (ObjectVTable*)&dog_vtable;  // ← Link to VTable!
    return self;
}

// MAIN - DEMONSTRATES DISPATCH
int main() {
    Dog* obj = Dog_create();
    
    // Dynamic dispatch through VTable:
    // 1. Load obj->base.vtable
    // 2. Cast to DogVTable*
    // 3. Call vtable->bark
    ((DogVTable*)obj->base.vtable)->bark((Object*)obj);
    
    ((ObjectVTable*)obj->base.vtable)->destroy((Object*)obj);
    return 0;
}

