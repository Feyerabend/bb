## vmo2.c

### Code Overview

1. Data Types and Structures:
* FieldType Enum: Defines two types of fields that an object can have: TYPE_INT and TYPE_FLOAT.
* Field Struct: Represents a field in an object, using a union to allow either an integer or a float value.
* Object Struct: Represents an object that has a name, an array of fields, a count of those fields, and (potentially) an array of method mnemonics.
* Instruction Enum: Defines the types of instructions the VM can execute, including operations like print, increment, addition, subtraction, multiplication, division, and halt.
* VMInstruction Struct: Represents a single instruction for the VM, containing the instruction type, the index of the field it operates on, and any operand needed for arithmetic operations.
* VirtualMachine Struct: Represents the VM itself, containing an array of instructions, the total count of those instructions, and a program counter (PC) that tracks the current instruction to execute.
2. Functionality:
* Field Operations: The code implements several functions to operate on the fields of an object:
* print_fields(Object *obj): Prints the name of the object and its fields.
* increment_field(Object *obj, int field_index): Increments an integer field at the specified index.
* add_to_field, subtract_from_field, multiply_field, divide_field: Perform arithmetic operations on integer fields, checking the type before performing the operation and handling potential errors (e.g., division by zero).
3. Object Creation:
* The create_object function allocates memory for a new object, initializes its fields, and sets its name. It also initializes the method count and methods array.
4. Virtual Machine Functions:
* The create_vm function allocates memory for a new VM, initializes it with a list of instructions, and sets the program counter to the start.
* The run_vm function executes the instructions stored in the VM, invoking appropriate functions based on the current instruction. The PC is incremented after each instruction until all instructions have been executed or a HALT instruction is encountered.
5. Program Building:
* The functions build_program_A and build_program_B create a series of VM instructions for two different objects, ObjectA and ObjectB. Each program includes print operations, arithmetic operations (add, subtract, multiply, divide), and is tailored to the fields of the corresponding object.
6. Main Functionality:
* The compile_and_run function orchestrates the entire process. It defines fields for two objects, creates these objects, builds their respective programs, runs the virtual machine for each object, and cleans up the allocated memory after execution to prevent memory leaks.

### Example Execution Flow

When main calls compile_and_run:

* It initializes ObjectA with integer and float fields, builds a program that manipulates ObjectA’s fields, and executes it.
* It then initializes ObjectB similarly, builds its program, and executes it.
* The output will display the results of the operations on each object, such as the values of their fields before and after arithmetic operations.

### Memory Management

The code ensures proper memory management by freeing all allocated memory for objects, fields, and programs at the end of the execution, which is essential in C to avoid memory leaks.

### Summary

Overall, this code provides a simple virtual machine environment for managing and manipulating objects with integer and float fields, demonstrating basic principles of memory management, object-oriented programming concepts in C, and virtual machine execution.

```
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

-----

## vmo3.c

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
    Fahrenheit.temperature = Celsius.temperature;   // Store converted temperature in Fahrenheit object
    PRINT Fahrenheit.temperature;                   // Print converted Fahrenheit temperature
}

// Define Program for Fahrenheit to Celsius conversion
Program ProgramFtoC {
    PRINT Fahrenheit.temperature;                    // Print original Fahrenheit temperature
    SUB Fahrenheit.temperature, 32.0;               // Subtract 32 from Fahrenheit temperature
    MUL Fahrenheit.temperature, 5.0 / 9.0;          // Multiply by 5/9 to convert to Celsius
    Celsius.temperature = Fahrenheit.temperature;    // Store converted temperature in Celsius object
    PRINT Celsius.temperature;                       // Print converted Celsius temperature
}
```
