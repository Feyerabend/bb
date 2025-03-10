
## Vtables

In object-oriented programming (OOP), *vtables* (virtual method tables) are a behind-the-scenes
mechanism (implementation) that enables *dynamic polymorphism*--the ability for objects of
different types to respond uniquely to the same method call.


### What Problem Do Vtables Solve?  

Imagine a scenario where a base class (e.g., "Animal") defines a general behavior (e.g., "makeSound()"),
and derived classes ("Cat" or "Dog") override this behavior with their own implementations. The challenge
arises when a program references an object *through its base type* (e.g., treating a "Cat" as an "Animal").
The system must still invoke the correct method ("Cat's makeSound()" instead of "Animal's default").
Vtables solve this by decoupling the method call from the specific implementation at compile time,
deferring the decision to runtime.


### How Do Vtables Work?  

1. *Table of Pointers*:  
   Each class that defines or inherits "overrideable" methods has its own vtable--a hidden table created
   at compile time. This table acts like a "menu" of function pointers, where each entry corresponds
   to one of the class's methods.  

2. *Object-Level Indirection*:  
   Every object instance contains a hidden pointer to its class's vtable. When a method is called (e.g.,
   "makeSound()"), the program follows this pointer to the vtable, looks up the appropriate entry, and
   executes the method associated with the object's *actual* type (not the reference type).  

3. *Inheritance and Overrides*:  
   When a subclass overrides a method, its vtable updates the corresponding entry to point to the new
   implementation. Unchanged methods retain pointers to their parent's implementations. This allows
   derived classes to reuse or refine behaviors while maintaining a consistent interface.


### Implications

- *Runtime Flexibility*: The correct method is resolved dynamically based on the object's true type,
  enabling polymorphic behaviour.  
- *Efficiency Trade-off*: While vtables add minimal memory overhead (one pointer per object) and a
  slight indirection cost during method calls, they optimise method dispatch compared to alternatives.  
- *Hierarchy Preservation*: Vtables reflect inheritance chains, ensuring methods are looked up in the
  correct order (e.g., parent classes before more distant ancestors).  


### Analogy

Think of a vtable as a restaurant menu tailored to a specific cuisine. Every dish (method) has a
standardised name (e.g., "Dessert"), but the actual recipe (implementation) depends on the restaurant
(object type). When you order "Dessert," the waiter (runtime system) checks the menu (vtable) linked
to the restaurant to serve the correct dish (execute the right method).  

In essence, vtables are the glue that lets objects "know" how to behave uniquely while adhering to a shared interface.


### Mapping Code to Vtable Concepts  

#### Original Example: `dog.c` from `compiler.py`

Looking at the compiled code `dog.c` from the original `compiler.py` and `dog.oo`:

```c
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
```

__1. Class Structure and Inheritance__

- The `Dog` struct embeds a `base` object (`Object`). This mimics inheritance: `Dog` *is-an* `Object`
  but adds its own traits.  
- The `DogVTable` extends `ObjectVTable`, reflecting how derived classes inherit and extend their
  parent's capabilities. The `bark` method is added here, while `destroy` is inherited.

__2. Vtable Creation__

- `dog_vtable` is a static table holding function pointers. This mirrors the "menu" analogy:
  - `destroy` points to a generic `object_destroy` (base class behavior).  
  - `bark` points to `Dog_bark` (derived class behavior).  
- This table is shared by all `Dog` instances, created once at compile time.

__3. Object Instantiation__

- `Dog_create()` allocates memory for a `Dog` and assigns its vtable pointer to `dog_vtable`.  
- Every `Dog` object now "knows" to use `Dog`'s methods (not `Object`'s) when a method is called.  

__4. Dynamic Method Dispatch__

- In `main()`, when `bark()` is called via `obj->base.vtable`, the vtable acts as a lookup table:  
  1. The object's vtable pointer (`dog_vtable`) is followed.  
  2. The `bark` entry in the table points to `Dog_bark`.  
  3. The correct function executes, even though the code treats the `Dog` as an `Object`.  
- This is runtime polymorphism: The system resolves `bark()` based on the object's true type
  (`Dog`), not the reference type (`Object`).

__5. Method Overrides__

- If a subclass of `Dog` (e.g., `Puppy`) overrode `bark()`, its vtable would replace the `bark`
  pointer with `Puppy_bark`. The vtable structure ensures the most specific implementation is called.


#### Extended Example: Generated Code from `compiler2.py`

Now, let's examine the more sophisticated implementation in `compiler2.py`. This version generates
C code from an abstract syntax tree (AST) that supports multiple classes, deeper inheritance, and
improved runtime safety. Here's an example of the generated code based on the sample AST:

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Object {
    struct ObjectVTable* vtable;
} Object;

typedef struct ObjectVTable {
    void (*destroy)(Object* self);
} ObjectVTable;

void object_destroy(Object* self) {
    printf("Object destroy: %p\n", (void*)self);
    if (self) free(self);
}

ObjectVTable object_vtable = { .destroy = object_destroy };

typedef struct Animal {
    Object base;
} Animal;

typedef struct AnimalVTable {
    ObjectVTable* base;
    void (*destroy)(Object* self);
    void (*speak)(Object* self);
} AnimalVTable;

void Animal_speak(Object* self) {
    printf("Animal sound\n");
}

void Animal_destroy(Object* self) {
    if (!self) return;
    printf("Animal destroy: %p, vtable: %p\n", (void*)self, (void*)self->vtable);
    object_destroy(self);
}

static AnimalVTable animal_vtable = {
    .base = &object_vtable,
    .destroy = Animal_destroy,
    .speak = Animal_speak,
};

Animal* Animal_create() {
    Animal* self = malloc(sizeof(Animal));
    if (!self) { printf("Memory allocation failed\n"); exit(1); }
    printf("Animal created: %p\n", (void*)self);
    self->base.vtable = (ObjectVTable*)&animal_vtable;
    return self;
}

typedef struct Dog {
    Animal base;
} Dog;

typedef struct DogVTable {
    AnimalVTable* base;
    void (*destroy)(Object* self);
    void (*speak)(Object* self);
} DogVTable;

void Dog_speak(Object* self) {
    printf("Woof!\n");
}

void Dog_destroy(Object* self) {
    if (!self) return;
    printf("Dog destroy: %p, vtable: %p\n", (void*)self, (void*)self->vtable);
    Animal_destroy(self);
}

static DogVTable dog_vtable = {
    .base = &animal_vtable,
    .destroy = Dog_destroy,
    .speak = Dog_speak,
};

Dog* Dog_create() {
    Dog* self = malloc(sizeof(Dog));
    if (!self) { printf("Memory allocation failed\n"); exit(1); }
    printf("Dog created: %p\n", (void*)self);
    self->base.base.vtable = (ObjectVTable*)&dog_vtable;
    return self;
}

int main() {
    Animal* animal = (Animal*)Dog_create();
    if (animal) ((AnimalVTable*)animal->base.vtable)->speak((Object*)animal);
    if (animal) { printf("Destroying animal: %p\n", (void*)animal); ((AnimalVTable*)animal->base.vtable)->destroy((Object*)animal); }
    return 0;
}
```

__1. Enhanced Class Structure and Inheritance__

- The `Animal` struct embeds an `Object` base, and `Dog` embeds an `Animal` base, forming a
  deeper inheritance chain (`Object` → `Animal` → `Dog`). This reflects a more realistic OOP hierarchy.
- Vtables are nested accordingly: `DogVTable` includes a pointer to `AnimalVTable`, which in
  turn points to `ObjectVTable`. This ensures the inheritance chain is preserved in the vtable structure.

__2. Vtable Creation with Base Pointers__

- Each vtable (`animal_vtable`, `dog_vtable`) explicitly links to its parent's vtable via the `.base`
  field. For example, `dog_vtable.base = &animal_vtable` connects `Dog` to `Animal`.
- This design allows the runtime to traverse the inheritance hierarchy if needed, though in this
  implementation, method resolution is direct via the object's vtable.

__3. Object Instantiation with Safety__

- Constructors like `Dog_create()` now include memory allocation checks (`if (!self)`), exiting
  on failure. This adds robustness compared to the simpler `Dog_create()` in `dog.c`.
- The vtable assignment accounts for deeper nesting: `self->base.base.vtable` reflects that `Dog`'s
  `Object` base is two levels up (`Dog` -> `Animal` -> `Object`).

__4. Dynamic Method Dispatch with Type Safety__

- In `main()`, an `Animal*` pointer holds a `Dog` object, simulating polymorphism. The call
  `((AnimalVTable*)animal->base.vtable)->speak((Object*)animal)`:
  1. Follows `animal->base.vtable` to `dog_vtable`.
  2. Finds `speak` overridden as `Dog_speak`.
  3. Executes `"Woof!\n"`, not `"Animal sound\n"`.
- The cast to `AnimalVTable*` ensures the code compiles even when treating the object as its
  base type, while the runtime resolves to the correct implementation.

__5. Destructor Chaining__

- Destructors (`Dog_destroy`, `Animal_destroy`) explicitly call their parent's destructor
  (e.g., `Animal_destroy(self)` in `Dog_destroy`). This ensures proper cleanup up the inheritance
  chain, ending with `object_destroy` freeing the memory.
- Null checks (`if (!self) return`) prevent crashes during destruction, enhancing reliability.

__6. Runtime Debugging Support__

- Constructors and destructors print object addresses and vtable pointers (e.g.,
  `printf("Dog destroy: %p, vtable: %p\n", ...)`). This aids debugging by tracking object lifecycles
  and vtable assignments.


### Takeaways from the Extended Example

- *Manual Vtable Construction*: Like the original, `compiler2.py` exposes the nuts and bolts of vtables
  that higher-level languages (C++, Java) hide. It generates explicit structs, function pointers,
  and vtable initialization.
- *Inheritance Depth*: The code supports multi-level inheritance (`Object` -> `Animal` -> `Dog`), with
  vtables reflecting the hierarchy via base pointers.
- *Destructor Chaining*: Explicit calls to parent destructors ensure proper resource cleanup,
  mimicking C++'s virtual destructor behavior.
- *Safety Enhancements*: Memory allocation checks and null pointer guards make the generated code more
  robust for real-world use.
- *Polymorphic Flexibility*: The `main()` function demonstrates assigning a `Dog` to an `Animal*`
  variable, with vtables ensuring the correct `speak()` is called.
- *Efficiency*: Despite added complexity, the overhead remains low--one vtable per class and one pointer
  per object, with direct method lookups.
- *Debugging Insight*: Printing object and vtable addresses provides visibility into runtime behavior,
  useful for understanding or troubleshooting.


### Comparing `compiler.py` and `compiler2.py`

- *Scalability*: `compiler2.py` handles multiple classes and arbitrary inheritance, while `compiler.py`
  was limited to a single `Dog` example.
- *Robustness*: The new version adds error handling and destructor chaining, absent in the original.
- *Flexibility*: The AST-driven approach in `compiler2.py` allows dynamic code generation for any class
  structure, unlike the hardcoded `dog.c`.


### Conclusion

The evolution from `compiler.py` to `compiler2.py` illustrates how vtables scale to support complex OOP
features in a low-level language like C. By mapping method calls to runtime-resolved function pointers,
vtables remain a lightweight, efficient solution for polymorphism. Whether manually crafted or generated,
they bridge the gap between static code and dynamic behavior, making them a cornerstone of OOP implementation.
