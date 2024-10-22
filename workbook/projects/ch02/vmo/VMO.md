
## vmo2.c

### Overview

1. Data Structures:
* FieldType Enum: Defines two types of fields: TYPE_INT for integers and TYPE_FLOAT for floating-point numbers.
* Field Struct: Represents a field within an object. It contains a type (from FieldType) and a union that holds either an integer or a float value, allowing flexibility in field types.
* Object Struct: Represents an object with:
* A name (string).
* An array of fields (Field).
* A count of fields.
* An array of method mnemonics (though this part is defined but not utilized in the provided code).
* A count of methods.
* Instruction Enum: Defines the instructions that the VM can execute, such as printing fields, performing arithmetic operations (increment, add, subtract, multiply, divide), and halting the execution.
* VMInstruction Struct: Represents a single instruction in the VM, consisting of the instruction type, the index of the field it acts on, and any additional operand for arithmetic instructions.
* VirtualMachine Struct: Contains an array of VM instructions, the total number of instructions, and the program counter (PC) which tracks the current instruction being executed.
2. Functions:
* Field Manipulation Functions: Functions for manipulating fields in objects, including printing fields, incrementing, adding, subtracting, multiplying, and dividing integer fields. Each function checks if the field type is appropriate before performing operations.
* Object Creation: The create_object function allocates memory for a new object, initializes its fields, and copies the provided fields.
* Virtual Machine Functions: Functions to create a VM and execute its instructions:
* create_vm initializes a VM with a list of instructions.
* run_vm executes the instructions sequentially, using a switch statement to determine which operation to perform based on the current instruction.
3. Program Building:
* The code includes functions build_program_A and build_program_B that create sequences of VM instructions to manipulate specific objects (ObjectA and ObjectB). Each program prints a field, modifies it with various arithmetic operations, and prints it again.
4. Main Execution:
* The compile_and_run function orchestrates the creation of two objects, builds their respective programs, creates and runs virtual machines for each program, and performs cleanup after execution. The function manages memory by freeing the allocated resources for the programs and objects to prevent memory leaks.
* The main function calls compile_and_run to execute the whole process.

Example Objects and Programs

* ObjectA:
* Fields: int field1 = 10, float field2 = 3.14
* Program: Print field1, then add 5, subtract 2, multiply by 3, divide by 2, and print field1 again.
* ObjectB:
* Fields: int field1 = 20, float field2 = 6.28
* Program: Print field1, increment it, add 10, and print field1 again.

### Memory Management

The code implements careful memory management by dynamically allocating memory for objects, fields, programs, and the virtual machine. It ensures that all allocated memory is freed at the end of execution to prevent memory leaks.

### Conclusion

This code serves as a simple demonstration of object-oriented programming concepts in C, including dynamic memory management, the use of unions for flexible data representation, and basic VM execution models. It provides a foundation that can be expanded to include more complex operations and features, such as method invocation and more advanced data types.

### Pseudo code

```simula
// Define ObjectA
Object ObjectA {
    int field1 = 10;
    float field2 = 3.14;
}

// Define ObjectB
Object ObjectB {
    int field1 = 20;
    float field2 = 6.28;
}

// Define Program for ObjectA
Program ProgramA {
    PRINT ObjectA.field1;            // Print field1 of ObjectA
    ADD ObjectA.field1, 5;           // Add 5 to field1 of ObjectA
    SUB ObjectA.field1, 2;           // Subtract 2 from field1 of ObjectA
    MUL ObjectA.field1, 3;           // Multiply field1 of ObjectA by 3
    DIV ObjectA.field1, 2;           // Divide field1 of ObjectA by 2
    PRINT ObjectA.field1;            // Print field1 of ObjectA again
}

// Define Program for ObjectB
Program ProgramB {
    PRINT ObjectB.field1;            // Print field1 of ObjectB
    INC ObjectB.field1;              // Increment field1 of ObjectB
    ADD ObjectB.field1, 10;          // Add 10 to field1 of ObjectB
    PRINT ObjectB.field1;            // Print field1 of ObjectB again
}
```


## vmo3.c

This code extends the previous with a practical example of converting temperatures between Celsius and Farenheit. In other respects it very much works in the same way.

Reviewing the pseudocode, one may notice (or imaginge) similarities to early object-oriented languages like Simula,[^simula] though it remains highly restricted in too many aspects. The pseudocode also illustrates concepts regarding how closely a programming language can be designed to reflect a virtual machine. Abstraction doesn’t always need to align with machine code; instead, it can operate at various levels depending on factors such as practicality, performance, and overall usefulness.

[^simula]: See https://en.wikipedia.org/wiki/Simula.

Furthermore, the choice of abstraction levels in virtual machines affects not only performance but also the ease with which a programmer can express complex ideas. While low-level instructions may offer precision and control, higher-level abstractions can simplify the development process, enabling more intuitive constructs without worrying about the underlying hardware. This balance between abstraction and control is a key consideration in the design of virtual machines and programming languages alike.


### Pseudo code

```
// Define Celsius Object
Object Celsius {
    float temperature = 25.0; // Example temperature in Celsius
}

// Define Fahrenheit Object
Object Fahrenheit {
    float temperature = 0.0;   // Placeholder for converted temperature
}

// Define Program for Celsius to Fahrenheit conversion
Program ProgramCtoF {
    PRINT Celsius.temperature;                     // Print original Celsius temperature
    MUL Celsius.temperature, 9.0 / 5.0;            // Multiply Celsius temperature by 9/5
    ADD Celsius.temperature, 32.0;                 // Add 32 to get Fahrenheit
    Fahrenheit.temperature = Celsius.temperature;  // Store converted temperature in Fahrenheit object
    PRINT Fahrenheit.temperature;                  // Print converted Fahrenheit temperature
}

// Define Program for Fahrenheit to Celsius conversion
Program ProgramFtoC {
    PRINT Fahrenheit.temperature;                   // Print original Fahrenheit temperature
    SUB Fahrenheit.temperature, 32.0;               // Subtract 32 from Fahrenheit temperature
    MUL Fahrenheit.temperature, 5.0 / 9.0;          // Multiply by 5/9 to convert to Celsius
    Celsius.temperature = Fahrenheit.temperature;   // Store converted temperature in Celsius object
    PRINT Celsius.temperature;                      // Print converted Celsius temperature
}
```
