
#include "oop_runtime.h"

typedef struct Dog {
    Object base;
} Dog;

typedef struct DogVTable {
    ObjectVTable base;
    void (*bark)(Object* self);
} DogVTable;

void Dog_bark(Object* self) {
    printf("Woof!\n");
}

DogVTable dog_vtable = {
    .base = { .destroy = object_destroy },
    .bark = Dog_bark,
};

Dog* Dog_create() {
    Dog* self = malloc(sizeof(Dog));
    self->base.vtable = (ObjectVTable*)&dog_vtable;
    return self;
}

int main() {
    Dog* obj = Dog_create();
    ((DogVTable*)obj->base.vtable)->bark((Object*)obj);
    DELETE(obj);
    return 0;
}
