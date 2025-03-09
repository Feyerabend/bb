
## Vtables

In object-oriented programming (OOP), *vtables* (virtual method tables) are a behind-the-scenes
mechanism (implementation) that enables *dynamic polymorphism*—the ability for objects of different types to
respond uniquely to the same method call.


### What Problem Do Vtables Solve?  

Imagine a scenario where a base class (e.g., "Animal") defines a general behavior (e.g. "makeSound()"),
and derived classes ("Cat" or "Dog") override this behavior with their own implementations. The challenge
arises when a program references an object *through its base type* (e.g., treating a "Cat" as an "Animal").
The system must still invoke the correct method ("Cat's makeSound()" instead of "Animal's default").
Vtables solve this by decoupling the method call from the specific implementation at compile time,
deferring the decision to runtime.


### How Do Vtables Work?  

1. *Table of Pointers*:  
   Each class that defines or inherits "overrideable" methods has its own vtable—a hidden table created
   at compile time. This table acts like a "menu" of function pointers, where each entry corresponds to
   one of the class's methods.  

2. *Object-Level Indirection*:  
   Every object instance contains a hidden pointer to its class's vtable. When a method is called (e.g.
   "makeSound()"), the program follows this pointer to the vtable, looks up the appropriate entry, and
   executes the method associated with the object's *actual* type (not the reference type).  

3. *Inheritance and Overrides*:  
   When a subclass overrides a method, its vtable updates the corresponding entry to point to the new
   implementation. Unchanged methods retain pointers to their parent's implementations. This allows
   derived classes to reuse or refine behaviors while maintaining a consistent interface.

### Implications

- *Runtime Flexibility*: The correct method is resolved dynamically based on the object's true type,
  enabling polymorphic behavior.  

- *Efficiency Trade-off*: While vtables add minimal memory overhead (one pointer per object) and a
  slight indirection cost during method calls, they optimize method dispatch compared to alternatives.  

- *Hierarchy Preservation*: Vtables reflect inheritance chains, ensuring methods are looked up in the
  correct order (e.g., parent classes before more distant ancestors).  


### Analogy

Think of a vtable as a restaurant menu tailored to a specific cuisine. Every dish (method) has a
standardised name (e.g., "Dessert"), but the actual recipe (implementation) depends on the restaurant
(object type). When you order "Dessert," the waiter (runtime system) checks the menu (vtable) linked
to the restaurant to serve the correct dish (execute the right method).  

In essence, vtables are the glue that lets objects "know" how to behave uniquely while adhering to a
shared interface.



### Mapping Code to Vtable Concepts  

Looking at the compliled code 'dog.c' from the 'compiler.py' and 'dog.oo':

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
    1. The object’s vtable pointer (`dog_vtable`) is followed.  
    2. The `bark` entry in the table points to `Dog_bark`.  
    3. The correct function executes, even though the code treats the `Dog` as an `Object`.  
- This is runtime polymorphism: The system resolves `bark()` based on the object's true type (`Dog`),
  not the reference type (`Object`).


__5. Method Overrides__
- If a subclass of `Dog` (e.g., `Puppy`) overrode `bark()`, its vtable would replace the `bark`
  pointer with `Puppy_bark`. The vtable structure ensures the most specific implementation is called.



### Takeaways from the Example  

- Manual vs. Automatic: In C, vtables are explicitly defined, while OOP languages hide this complexity.
  The code shows the "scaffolding" that languages like C++/Java automate.  

- Shared Vtables: All instances of `Dog` share the same vtable, minimizing memory overhead.  

- Type Flexibility: The code treats `Dog` as an `Object` but still invokes `Dog`-specific behavior.
  This mirrors polymorphism in OOP (e.g., storing different animals in an `Animal[]`).  

- Destructor Handling: The `DELETE` macro likely calls `destroy()` from the vtable, demonstrating
  *polymorphic cleanup*.

- Code Reuse: Inherited methods (e.g., `destroy`) need not be reimplemented.  

- Flexible Abstraction: Objects can be treated generically while retaining unique behaviors.  

- Efficiency: Vtables add minimal overhead compared to brute-force approaches (e.g., `if/else` chains to check types).  

This hands-on illustration reinforces how vtables are the "invisible glue" making polymorphism practical and efficient in OOP.
