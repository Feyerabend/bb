
## Decorator Design Pattern

The Decorator design pattern is a structural pattern that allows you to add new behaviors to objects dynamically
without altering their existing code. It provides a flexible alternative to subclassing for extending functionality.

The main idea behind the Decorator pattern is to "wrap" an existing object (the component) with one or more decorator
objects. Each decorator adds its own behavior before or after delegating the request to the wrapped component. This
creates a chain of responsibility, where each decorator in the chain adds a specific functionality.

* *To add responsibilities to individual objects dynamically and transparently:* without affecting other objects.
* *For responsibilities that can be withdrawn:* Decorators can be added and removed at runtime.
* *When extension by subclassing is impractical:* Sometimes, inheritance can lead to a "class explosion" if you have
  many independent features that can be combined in various ways. Decorators offer a more flexible solution.


### Structure

The Decorator pattern typically involves the following participants:

1. *Component:* Defines the interface for objects that can have responsibilities added to them.
2. *Concrete Component:* Implements the `Component` interface. This is the original object to which new behaviors
   will be added.
3. *Decorator:* An abstract class that maintains a reference to a `Component` object and conforms to the `Component`
   interface. It mirrors the `Component` interface.
4. *Concrete Decorator:* Implements the `Decorator` interface and adds specific responsibilities. It typically
   delegates to the wrapped `Component` object and then adds its own unique behavior.


### Advantages & Disadvantages

* *Flexibility:* You can mix and match different decorators to achieve various combinations of behaviors.
* *Open/Closed Principle:* You can extend an object's functionality without modifying its existing code (open
  for extension, closed for modification).
* *Avoids Class Explosion:* Instead of creating numerous subclasses for every possible combination of features,
  you can dynamically compose behaviors.
* *Single Responsibility Principle:* Each decorator can focus on a single added responsibility.

* *Increased Complexity:* A large number of small, similar objects can make the design harder to understand.
* *Identity Issues:* Decorators add layers of objects. If you rely on object identity (e.g., checking
  `obj1 is obj2`), this can become tricky.


### Examples

Let's imagine a coffee shop where you can order different types of coffee and add various condiments.

```python
# 1. Component Interface
class Coffee:
    def get_cost(self):
        pass

    def get_description(self):
        pass

# 2. Concrete Component
class SimpleCoffee(Coffee):
    def get_cost(self):
        return 5.0

    def get_description(self):
        return "Simple Coffee"

# 3. Decorator (Abstract)
class CoffeeDecorator(Coffee):
    def __init__(self, decorated_coffee):
        self._decorated_coffee = decorated_coffee

    def get_cost(self):
        return self._decorated_coffee.get_cost()

    def get_description(self):
        return self._decorated_coffee.get_description()

# 4. Concrete Decorators
class MilkDecorator(CoffeeDecorator):
    def __init__(self, decorated_coffee):
        super().__init__(decorated_coffee)

    def get_cost(self):
        return super().get_cost() + 1.5

    def get_description(self):
        return super().get_description() + ", Milk"

class SugarDecorator(CoffeeDecorator):
    def __init__(self, decorated_coffee):
        super().__init__(decorated_coffee)

    def get_cost(self):
        return super().get_cost() + 0.5

    def get_description(self):
        return super().get_description() + ", Sugar"

class CaramelDecorator(CoffeeDecorator):
    def __init__(self, decorated_coffee):
        super().__init__(decorated_coffee)

    def get_cost(self):
        return super().get_cost() + 2.0

    def get_description(self):
        return super().get_description() + ", Caramel"

# Client
if __name__ == "__main__":
    my_coffee = SimpleCoffee()
    print(f"Order: {my_coffee.get_description()}, Cost: ${my_coffee.get_cost()}")

    my_coffee = MilkDecorator(my_coffee)
    print(f"Order: {my_coffee.get_description()}, Cost: ${my_coffee.get_cost()}")

    my_coffee = SugarDecorator(my_coffee)
    print(f"Order: {my_coffee.get_description()}, Cost: ${my_coffee.get_cost()}")

    my_coffee = CaramelDecorator(my_coffee)
    print(f"Order: {my_coffee.get_description()}, Cost: ${my_coffee.get_cost()}")

    # Order: Coffee with milk and sugar
    another_coffee = SimpleCoffee()
    another_coffee = MilkDecorator(another_coffee)
    another_coffee = SugarDecorator(another_coffee)
    print(f"\nAnother Order: {another_coffee.get_description()}, Cost: ${another_coffee.get_cost()}")
```


#### C++ Example: Text Formatting

Implementing the Decorator design pattern in plain C is less straightforward than in object-oriented languages
like Python or C++ because C lacks built-in features like classes, inheritance, and polymorphism. However, the
core principles can still be applied using structs and function pointers to achieve a similar effect of
dynamically adding behavior.


### Decorator Design Pattern in Plain C

In plain C, the Decorator pattern is typically achieved through a combination of:

* *Structs:* To represent the "objects" (components and decorators) and their data.
* *Function Pointers:* To simulate virtual methods and allow decorators to "wrap" and call the original
  component's functions.
* *Encapsulation (Manual):* Carefully managing pointers within structs to create the composition hierarchy.


### Core Idea in C

The fundamental idea remains: to add new responsibilities to an object dynamically. In C, this means:

1. *Defining a common interface:* This will be a `struct` that contains function pointers representing the
   operations of the component.
2. *Concrete Components:* These will be structs that implement the common interface by providing actual
   function implementations for the function pointers.
3. *Decorators:* These will also be structs that contain a pointer to the "decorated" component (which
   also conforms to the common interface). They will then provide their own function implementations that
   typically call the decorated component's functions and add their own logic.


### Structure (Conceptual in C)

1.  *Component Interface (Common Struct):*
    ```c
    typedef struct Component {
        // Function pointers representing the operations
        // e.g., double (*get_cost)(struct Component* self);
        //       char* (*get_description)(struct Component* self);
        void (*operation)(struct Component* self); // A generic operation example
        // .. potentially other common data
    } Component;
    ```

2.  *Concrete Component (Specific Struct and Functions):*
    ```c
    typedef struct ConcreteComponent {
        Component base; // Embed the Component interface
        // Specific data for this component
        char* name;
    } ConcreteComponent;

    // Functions implementing the Component operations for ConcreteComponent
    void concrete_component_operation(Component* self);
    // .. init function for ConcreteComponent
    ```

3.  *Decorator (Abstract - conceptual, typically a pattern for Concrete Decorators):*
    ```c
    typedef struct Decorator {
        Component base; // Embed the Component interface
        Component* decorated_component; // Pointer to the wrapped component
    } Decorator;

    // Decorator functions typically call the decorated_component's functions
    // and then add their own logic.
    ```

4.  *Concrete Decorator (Specific Struct and Functions):*
    ```c
    typedef struct ConcreteDecoratorA {
        Decorator base; // Embed the Decorator (which embeds Component)
        // Specific data for this decorator (if any)
    } ConcreteDecoratorA;

    // Functions implementing the Component operations for ConcreteDecoratorA
    void concrete_decorator_a_operation(Component* self);
    // ... init function for ConcreteDecoratorA
    ```


### Advantages in C

* *Runtime Flexibility:* Behavior can be added or removed at runtime by changing the chain of decorators.
* *Avoids "Class Explosion":* Reduces the need for many specialized structs to cover all combinations of features.
* *Separation of Concerns:* Each decorator handles a specific, single responsibility.

### Disadvantages in C

* *Complexity:* Requires careful manual memory management and explicit handling of function pointers,
  which can make the code harder to read and debug compared to object-oriented languages.
* *Lack of Type Safety:* Without compiler-enforced inheritance, it's easier to make errors if you don't
  consistently use the `Component` interface struct.
* *Verbosity:* More boilerplate code is needed to set up the "objects" and their "methods."


### Example: Text Formatting in Plain C

Let's adapt the text formatting example. We'll define a `Text` interface with a `get_content` function.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// fwd decl
typedef struct Text Text;

// 1. Component Interface
struct Text {
    // Function pointer for the main operation
    char* (*get_content)(Text* self);
    // A destructor-like function for cleanup (important in C)
    void (*destroy)(Text* self);
};

// --- Concrete Component: SimpleText ---

typedef struct SimpleText {
    Text base; // Embed the Text interface
    char* content;
} SimpleText;

char* simple_text_get_content(Text* self) {
    SimpleText* st = (SimpleText*)self;
    // Return a copy to avoid modification of internal state and allow free() by caller
    return strdup(st->content);
}

void simple_text_destroy(Text* self) {
    SimpleText* st = (SimpleText*)self;
    free(st->content);
    free(st);
}

Text* simple_text_create(const char* initial_content) {
    SimpleText* st = (SimpleText*)malloc(sizeof(SimpleText));
    if (st == NULL) {
        perror("Failed to allocate SimpleText");
        return NULL;
    }
    st->base.get_content = simple_text_get_content;
    st->base.destroy = simple_text_destroy;
    st->content = strdup(initial_content);
    if (st->content == NULL) {
        perror("Failed to duplicate content");
        free(st);
        return NULL;
    }
    return (Text*)st;
}

// --- Decorator (Base Structure) ---

typedef struct TextDecorator {
    Text base; // Embed the Text interface
    Text* decorated_text; // Pointer to the wrapped text
} TextDecorator;

// Common destructor for decorators
void text_decorator_destroy(Text* self) {
    TextDecorator* td = (TextDecorator*)self;
    td->decorated_text->destroy(td->decorated_text); // Destroy the wrapped object
    free(td);
}

// --- Concrete Decorators ---

// Bold Text Decorator
typedef struct BoldTextDecorator {
    TextDecorator base;
} BoldTextDecorator;

char* bold_text_get_content(Text* self) {
    BoldTextDecorator* btd = (BoldTextDecorator*)self;
    char* original_content = btd->base.decorated_text->get_content(btd->base.decorated_text);
    if (original_content == NULL) return NULL;

    size_t new_len = strlen(original_content) + strlen("<b></b>") + 1;
    char* result = (char*)malloc(new_len);
    if (result == NULL) {
        perror("Failed to allocate bold text");
        free(original_content);
        return NULL;
    }
    snprintf(result, new_len, "<b>%s</b>", original_content);
    free(original_content); // Free the content returned by the decorated object
    return result;
}

Text* bold_text_decorator_create(Text* decorated_text) {
    BoldTextDecorator* btd = (BoldTextDecorator*)malloc(sizeof(BoldTextDecorator));
    if (btd == NULL) {
        perror("Failed to allocate BoldTextDecorator");
        decorated_text->destroy(decorated_text); // Clean up in case of failure
        return NULL;
    }
    btd->base.base.get_content = bold_text_get_content;
    btd->base.base.destroy = text_decorator_destroy; // Use common decorator destructor
    btd->base.decorated_text = decorated_text;
    return (Text*)btd;
}

// Italic Text Decorator
typedef struct ItalicTextDecorator {
    TextDecorator base;
} ItalicTextDecorator;

char* italic_text_get_content(Text* self) {
    ItalicTextDecorator* itd = (ItalicTextDecorator*)self;
    char* original_content = itd->base.decorated_text->get_content(itd->base.decorated_text);
    if (original_content == NULL) return NULL;

    size_t new_len = strlen(original_content) + strlen("<i></i>") + 1;
    char* result = (char*)malloc(new_len);
    if (result == NULL) {
        perror("Failed to allocate italic text");
        free(original_content);
        return NULL;
    }
    snprintf(result, new_len, "<i>%s</i>", original_content);
    free(original_content);
    return result;
}

Text* italic_text_decorator_create(Text* decorated_text) {
    ItalicTextDecorator* itd = (ItalicTextDecorator*)malloc(sizeof(ItalicTextDecorator));
    if (itd == NULL) {
        perror("Failed to allocate ItalicTextDecorator");
        decorated_text->destroy(decorated_text);
        return NULL;
    }
    itd->base.base.get_content = italic_text_get_content;
    itd->base.base.destroy = text_decorator_destroy;
    itd->base.decorated_text = decorated_text;
    return (Text*)itd;
}

// --- Client ---
int main() {
    // Create a simple text
    Text* my_text = simple_text_create("Hello C World");
    if (my_text == NULL) return 1;

    char* content = my_text->get_content(my_text);
    printf("Original: %s\n", content);
    free(content); // Always free content returned by get_content

    // Decorate with Bold
    Text* bold_text = bold_text_decorator_create(my_text); // my_text is now owned by bold_text
    if (bold_text == NULL) { my_text->destroy(my_text); return 1; } // Clean up if decorator creation fails

    content = bold_text->get_content(bold_text);
    printf("Bold: %s\n", content);
    free(content);

    // Decorate with Italic on top of Bold
    Text* bold_italic_text = italic_text_decorator_create(bold_text); // bold_text is now owned by bold_italic_text
    if (bold_italic_text == NULL) { bold_text->destroy(bold_text); return 1; } // Clean up if decorator creation fails

    content = bold_italic_text->get_content(bold_italic_text);
    printf("Bold and Italic: %s\n", content);
    free(content);

    // Chain decorators directly
    Text* another_text = simple_text_create("Chain Me!");
    if (another_text == NULL) return 1;

    Text* chained_text = bold_text_decorator_create(another_text);
    if (chained_text == NULL) { another_text->destroy(another_text); return 1; }

    chained_text = italic_text_decorator_create(chained_text);
    if (chained_text == NULL) { if (chained_text) chained_text->destroy(chained_text); return 1; }


    content = chained_text->get_content(chained_text);
    printf("Chained: %s\n", content);
    free(content);


    // Clean up all allocated memory for the final decorator in the chain
    bold_italic_text->destroy(bold_italic_text); // This will recursively destroy bold_text and my_text
    chained_text->destroy(chained_text); // This will recursively destroy the bold decorator and another_text

    return 0;
}
```

*Explanation for the C Example:*

* *`struct Text`:* This acts as our "interface." It contains function pointers (`get_content` and `destroy`)
  that all "Text" objects (simple texts and decorators) must implement.

* *`SimpleText`:* This is our concrete component. It embeds a `Text` struct as its `base` member. Its
  `get_content` and `destroy` functions are assigned to `base.get_content` and `base.destroy` respectively
  during creation.

* *`TextDecorator`:* This is a conceptual base for all decorators. It also embeds a `Text` struct (`base`)
  and critically holds a pointer `decorated_text` to the `Text` object it's wrapping.

* *`BoldTextDecorator`, `ItalicTextDecorator`:* These are our concrete decorators. They embed `TextDecorator`
  and provide their own `get_content` implementations. These implementations call the `get_content` of the
  `decorated_text` and then add their specific formatting (`<b>`, `<i>`).

* *Creation Functions (`_create`):* These functions are essential for instantiating our "objects." They allocate
  memory, initialize the `base` `Text` struct's function pointers, and set up any specific data.

* *Memory Management (`destroy`):* This is crucial in C. Each `Text` object (component or decorator) is
  responsible for freeing its own resources and, in the case of decorators, recursively calling `destroy`
  on the `decorated_text` to ensure the entire chain is cleaned up. `get_content` returns a `strdup`'d
  string, so the caller is responsible for `free`ing the returned string.

This C implementation, while more verbose and requiring careful manual memory management, effectively demonstrates
the Decorator pattern's ability to dynamically compose behaviors.
