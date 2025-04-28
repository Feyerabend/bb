#include <stdio.h>

typedef struct {
    void (*speak)(void*);
} Animal;

typedef struct {
    Animal base;
} Dog;

typedef struct {
    Animal base;
} Cat;

void dog_speak(void *self) { printf("Woof\n"); }
void cat_speak(void *self) { printf("Meow\n"); }

void animal_init(Animal *a, void (*speak)(void*)) {
    a->speak = speak;
}

int main() {
    Dog dog;
    Cat cat;
    animal_init(&dog.base, dog_speak);
    animal_init(&cat.base, cat_speak);

    Animal *animals[] = {&dog.base, &cat.base};
    for (int i = 0; i < 2; i++) {
        animals[i]->speak(animals[i]); // Output: Woof, Meow
    }
    return 0;
}