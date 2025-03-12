
## Ideas for a Simple OOP Language

### Features of the Language

1. *Classes and Objects*:
   - Define classes with attributes and methods.
   - Instantiate objects from classes.

2. *Encapsulation*:
   - Support public and private members (e.g., `public` and `private` keywords).

3. *Inheritance*:
   - Allow classes to inherit from other classes.

4. *Polymorphism*:
   - Support method overriding and dynamic dispatch.

5. *Constructors and Destructors*:
   - Automatically generate initialization and cleanup code.

6. *Simple Syntax*:
   - Keep the syntax clean and easy to understand.



### Example Language Syntax
Here's an example of what the language might look like:

```java
// define a class
class Animal {
    private:
        string name;

    public:
        // constructor
        Animal(string name) {
            this.name = name;
        }

        // method
        void speak() {
            print("Animal sound");
        }
}

// inheritance
class Dog : Animal {
    public:
        // constructor
        Dog(string name) : Animal(name) {}

        // method overriding
        void speak() {
            print(this.name + " says woof!");
        }
}

// polymorphism
void makeSound(Animal animal) {
    animal.speak();
}

void main() {
    Dog myDog = Dog("Buddy");
    makeSound(myDog);  // dynamic dispatch
}
```


### Compilation to C

The compiler would translate the above language into C code. Here's how the concepts would map:

__1. *Classes and Objects*__

- A class becomes a `struct` in C.
- Methods become functions that take the object (`this` pointer) as their first argument.


```c
// Generated C code for the Animal class
typedef struct {
    char* name;
} Animal;

void Animal_init(Animal* this, const char* name) {
    this->name = strdup(name);
}

void Animal_speak(Animal* this) {
    printf("Animal sound\n");
}
```


__2. *Inheritance*__

- Inheritance is implemented by embedding the parent struct in the child struct.

```c
// generated C code for the Dog class
typedef struct {
    Animal base;  // embed the parent struct
} Dog;

void Dog_init(Dog* this, const char* name) {
    Animal_init((Animal*)this, name);  // call parent constructor
}

void Dog_speak(Dog* this) {
    printf("%s says woof!\n", ((Animal*)this)->name);
}
```

__3. *Polymorphism*__

- Use function pointers in the struct to support dynamic dispatch.

```c
// add a function pointer to the struct
typedef struct {
    char* name;
    void (*speak)(void*);  // function pointer for polymorphism
} Animal;

void Animal_speak(Animal* this) {
    printf("Animal sound\n");
}

void Dog_speak(Dog* this) {
    printf("%s says woof!\n", ((Animal*)this)->name);
}

// init function pointers
void Dog_init(Dog* this, const char* name) {
    Animal_init((Animal*)this, name);
    ((Animal*)this)->speak = (void (*)(void*))Dog_speak;  // override method
}
```

__4. *Encapsulation*__

- Use opaque pointers and separate header/source files to hide private members.

```c
// dog.h
typedef struct Dog Dog;

Dog* Dog_create(const char* name);
void Dog_speak(Dog* self);
void Dog_destroy(Dog* self);

// dog.c
#include "dog.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Dog {
    Animal base;  // private members are hidden
};

Dog* Dog_create(const char* name) {
    Dog* self = (Dog*)malloc(sizeof(Dog));
    Animal_init((Animal*)self, name);
    ((Animal*)self)->speak = (void (*)(void*))Dog_speak;
    return self;
}

void Dog_speak(Dog* self) {
    printf("%s says woof!\n", ((Animal*)self)->name);
}

void Dog_destroy(Dog* self) {
    free(self);
}
```

__5. *Main Program*__

- The main program is translated into a C `main` function.

```c
int main() {
    Dog* myDog = Dog_create("Buddy");
    ((Animal*)myDog)->speak(myDog);  // polymorphism
    Dog_destroy(myDog);
    return 0;
}
```


### Compiler Design
The compiler would have the following components:

1. *Lexer*: Tokenizes the input code.

2. *Parser*: Builds an abstract syntax tree (AST) from the tokens.

3. *Semantic Analyzer*: Checks for correctness (e.g., type checking).

4. *Code Generator*: Translates the AST into C code.



### Example Compiler Workflow

__1. *Input (Custom Language)*:__

   ```plaintext
   class Dog : Animal {
       public:
           Dog(string name) : Animal(name) {}
           void speak() {
               print(this.name + " says woof!");
           }
   }
   ```

__2. *Output (C Code)*:__

   ```c
   typedef struct {
       Animal base;
   } Dog;

   void Dog_init(Dog* this, const char* name) {
       Animal_init((Animal*)this, name);
       ((Animal*)this)->speak = (void (*)(void*))Dog_speak;
   }

   void Dog_speak(Dog* this) {
       printf("%s says woof!\n", ((Animal*)this)->name);
   }
   ```



### Summary

By designing a simple language with classes, inheritance, and polymorphism,
and compiling it to C, you can demonstrate how OOP concepts work under the hood.
The key is to map high-level OOP constructs to C constructs like structs,
function pointers, and manual memory management. This approach keeps the
language simple while still showcasing the power of OOP.
