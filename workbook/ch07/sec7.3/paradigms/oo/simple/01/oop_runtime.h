#ifndef OOP_RUNTIME_H
#define OOP_RUNTIME_H

#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// base object (only holds the vtable)
typedef struct Object {
    struct ObjectVTable* vtable;
} Object;

// base vtable (includes destroy)
typedef struct ObjectVTable {
    void (*destroy)(void* self);
} ObjectVTable;

// default destructor (frees memory)
void object_destroy(void* self) {
    free(self);
}

// macros
#define NEW(T, ...) T##_create(__VA_ARGS__)
#define CALL(obj, method) ((obj)->vtable->method((Object*)obj))
#define DELETE(obj) ((Object*)obj)->vtable->destroy((Object*)obj)

#endif  // OOP_RUNTIME_H
