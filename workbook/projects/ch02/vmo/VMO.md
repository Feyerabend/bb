## Project

*Build from the code, add more mathematical functions, more data types, etc.*

*Prerequisties: Some familiarity with concepts in object-orientation. Preferably you know some different approaches to how objects are handled in various languages, which can be useful for expanding the code.*

### Overview

1. Data Structures:
* Field Type Definition: Defines the types of fields within an object, including types for integers and floating-point numbers.
* Field Structure: Represents a field within an object and contains:
* A name (string).
* A type indicating whether it's an integer or a float.
* A value, which can be either an integer or a float, allowing flexibility.
* Object Structure: Represents an object that includes:
* A name (string).
* An array of fields (Field).
* A count of fields.
* Method Definition: Describes methods that can be associated with objects (though not utilized explicitly in the code).
2. Functions:
* Field Manipulation Functions: Functions that allow for operations on fields, such as printing field values and modifying them through addition.
* Object Creation Function: Allocates memory for a new object, initializes its fields, and sets up the object's properties.
* Method Definition: Defines methods for object behavior, such as adding a value to a field and printing field values.
3. Program Building:
* Main Execution Method: Defines a method that manages the program's core logic:
* Prints the initial value of a field.
* Modifies the field by adding a specific value (e.g., adding 5).
* Prints the updated field value.
4. Main Execution:
* Program Initialization: The main function creates an object with specific fields, calls the method to execute the addition, and manages the flow of execution.
* Method Invocation: Calls the method to perform actions defined within the object, such as adding a value to a field.


### Example Object and Program

ExampleObject:

Fields:
* `field1`: float initialized to 10.0.
* `field2`: int initialized to 20 (though not actively used in this specific example).

Program:
* Print field1, add 5 to field1, and print field1 again.


### Memory Management

The code includes careful memory management by dynamically allocating resources for objects. It ensures that any necessary memory is appropriately freed after execution, thus preventing memory leaks.

### Pseudo code

```
// Simple addition program

object ExampleObject {
    field field1: float = 10.0;  // Initial value of the first field
    field field2: int = 20;       // Initial value of the second field

    method addValue() {
        print(field1);             // Print the initial value of field1
        field1 = field1 + 5.0;     // Add 5 to field1
        print(field1);             // Print the updated value of field1
    }
}

ExampleObject.addValue();  // Call the addValue method
```

### Conclusion

This code serves as a straightforward demonstration of object-oriented concepts in C, emphasizing basic operations on fields within an object. It highlights method invocation and manipulation of data types, providing a foundation for further enhancements and more complex functionality. Future improvements could involve implementing more advanced arithmetic operations, additional methods, and broader data types.

Reviewing the pseudocode, one may notice (or imaginge) similarities to early object-oriented languages like Java,[^java] though it remains both highly volatile and restricted in too many aspects. It is e.g. scary from an object-oriented view of encapsulation. The pseudocode also illustrates concepts regarding how closely a programming language can be designed to reflect a virtual machine. Abstraction doesn’t always need to align with machine code; instead, it can operate at various levels depending on factors such as practicality, performance, and overall usefulness.

[^java]: See https://en.wikipedia.org/wiki/Java_(programming_language).

Furthermore, the choice of abstraction levels in virtual machines affects not only performance but also the ease with which a programmer can express complex ideas. While low-level instructions may offer precision and control, higher-level abstractions can simplify the development process, enabling more intuitive constructs without worrying about the underlying hardware. This balance between abstraction and control is a key consideration in the design of virtual machines and programming languages alike.

