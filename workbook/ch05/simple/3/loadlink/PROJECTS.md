
## Projects for Linker/Loader

### Exercises

1. Fixed-Point Arithmetic Integration:
    - Task: Extend the program to load and use the FixedPoint class in the VM. Write test cases
      to ensure operations like addition, subtraction, multiplication, and division are correctly
      handled with FixedPoint numbers.
	- Goal: Modify your program to include operations with fixed-point numbers. Ensure that arithmetic
      operations return the correct results by testing edge cases like overflows, precision errors,
      and division by zero.

2. Linker and Loader Enhancements:
	- Task: Modify the LibraryLoader class to handle both dynamic and static libraries. The dynamic
      libraries (like the existing factorial or fibonacci) will be linked at runtime, while the static
      library (like the FixedPoint class) will be loaded directly as a module during the initial load.
	- Goal: Learn the differences between dynamic and static libraries. Implement logic that distinguishes
      between static (preloaded) and dynamic (runtime-loaded) libraries and handles them appropriately.

3. Fixed-Point Math in VM Program:
    - Task: Add a new program that uses FixedPoint math operations. For example, write a program that
      computes the fixed-point square root of a number using the sqrt_fixed function.
	- Goal: Extend your VM to support floating-point and fixed-point operations together. Test with a
      program that calls sqrt_fixed or performs a series of arithmetic operations with FixedPoint.

4. Extend FixedPoint with More Functions:
	- Task: Add additional math functions to the FixedPoint class, such as pow, log, and sin (using a
      small approximation for the sine function, e.g., via a series expansion). Then, integrate those
      functions into the VM by adding new operations that call these functions.
	- Goal: This will help you extend the existing VM and library loader while also gaining a deeper
      understanding of fixed-point math.

5.	Memory Management for Fixed-Point Operations:
	- Task: Implement memory management for operations involving FixedPoint numbers. You will need to
      allocate, store, and retrieve these values efficiently from the VM's memory. Consider using a
      stack-based approach for temporary values during operations.
	- Goal: Understand how fixed-point numbers can be managed in a stack-based virtual machine and how
      memory management affects performance and resource usage.

6.	Debugging the VM with Fixed-Point Support:
	- Task: Implement a debugging feature in the VM that tracks and logs the state of fixed-point
      registers or memory locations. For example, you can print out the result of FixedPoint operations
      and monitor the values during program execution.
	- Goal: Learn how to add debugging features to your VM, making it easier to trace and monitor the
      behavior of fixed-point math.

7.	Performance Benchmarking:
	- Task: Create a benchmarking program that compares the performance of arithmetic operations between
      floating-point and fixed-point calculations. Test operations like addition, multiplication, and
      division, and compare the results in terms of speed and accuracy.
	- Goal: Explore the trade-offs between fixed-point and floating-point arithmetic. Investigate when
      each type of arithmetic is preferable and measure performance differences.


### Projects

1.	Static and Dynamic Library System:
	- Project: Develop a full-fledged system that can dynamically load libraries at runtime (like factorial
      and fibonacci), while also supporting static libraries (like FixedPoint). Ensure that the VM can link
      to both types of libraries, call functions from them, and handle them correctly.
	- Goal: Learn how linking and loading work in programming environments. By building both dynamic and
      static linking features, you'll gain hands-on experience in managing program dependencies.

2.	Fixed-Point Math Extension with Trigonometric Functions:
	- Project: Extend the FixedPoint class with support for more advanced mathematical functions, such as
      trigonometric functions (sin, cos, tan). Implement these using fixed-point approximations or the much simpler:
      lookup tables. Then, create a VM program that computes these functions and visualize the results
      (e.g. plotting sine waves).
	- Goal: Deepen your understanding of both fixed-point arithmetic and VM programming. This will also
      involve research into how to efficiently approximate functions like trigonometric ones using fixed-point
      representations.

3.	VM with a Plugin System for Libraries:
	- Project: Create a plugin system within the VM, where new libraries can be dynamically added, removed,
      and swapped at runtime without modifying the core VM. Implement a system where the user can provide a
      path to a Python file containing a library, and the VM loads it automatically.
	- Goal: Gain experience in building modular systems where external components (like libraries) can be
      easily integrated. This project teaches you about runtime flexibility and extensibility in software design.

4.	Virtual Machine with Graphical User Interface (GUI):
	- Project: Create a simple GUI application (using a library like Tkinter or PyQt) that visualizes the
      VM's execution process, including step-by-step program execution, variable values, and stack contents.
      You can also include a graphical interface to load and run programs dynamically, as well as inspect
      results for fixed-point operations.
	- Goal: Learn how to create interactive software and how to represent a virtual machine's state visually.
      This is a great project if you want to combine low-level programming with user interface design.

5.	Optimization of Fixed-Point Calculations in the VM:
	- Project: Analyze the performance of fixed-point operations within the VM and optimize them. For example,
      you could replace some FixedPoint operations with more efficient algorithms, optimize memory usage, or
      reduce the number of operations for specific calculations.
	- Goal: Focus on performance and optimization. This project would help you explore ways to make fixed-point
      arithmetic more efficient in a virtual machine environment.

6.	Cross-Library Integration Project:
	- Project: Write a complex program that makes use of both the factorial and fibonacci libraries, while also
      performing operations with fixed-point numbers. The program can compute values like fibonacci(n) * factorial(m)
      using both libraries and fixed-point arithmetic.
	- Goal: Practice integrating multiple libraries with different types of data and operations in your VM.
      You will also learn to deal with more complex dependencies and ensure compatibility between different types
      of libraries.

These tasks and projects build on your existing understanding of VM programming, static and dynamic libraries,
and fixed-point arithmetic.
