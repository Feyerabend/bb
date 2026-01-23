
## Linking and Loading

- Linker: The LibraryLoader serves as the linker in this case. It dynamically resolves
  references (function calls like factorial or fibonacci) and ensures that the virtual
  machine knows how to find and call the correct functions in the libraries.

- Loader: The LibraryLoader also acts as the loader, which loads the actual library code
  into memory during execution. This step ensures the code is available for use by the
  virtual machine while the program is running.

- Virtual Machine (VM): The virtual machine is the "execution environment" where the
  program runs. It executes the instructions (e.g., assignments, function calls) and
  uses the libraries that have been linked and loaded dynamically. The VM abstract
  away the underlying hardware and makes the program run on a virtualised environment.

#### Linking

Linking is the process of combining various pieces of code (such as object files or libraries)
to create an executable program. There are two primary types:

- Static Linking: This occurs at compile-time, where all code from libraries is combined into
  the executable. It's done before the program runs.

- Dynamic Linking: This occurs at runtime, where the necessary libraries are loaded into memory
  when the program is executed. The linking process establishes references to functions and variables
  from the linked libraries.

In the context of the program, dynamic linking is being used. The libraries (factorial_library and
fibonacci_library) are not included directly in the main program at compile time but are loaded and
linked into the virtual machine at runtime using the LibraryLoader and the link_library() method.


#### Loading

Loading is the process of bringing code (such as libraries or executable files) into memory so that
it can be executed by the system. The loader is responsible for setting up the program's memory space,
adjusting addresses, and ensuring that functions can be called and variables accessed at runtime.

In this case, dynamic loading is done by the LibraryLoader class. The loader takes the libraries and
makes them available to the virtual machine (vm) during execution. It's a way to ensure that the
program has access to the necessary code (in this case, the factorial and Fibonacci functions) without
needing to be statically compiled together.


### Summary 

This code is an illustration of dynamic linking and loading in the context of a virtual machine running
a program. The program uses external libraries (factorial and Fibonacci), and these libraries are linked
and loaded dynamically at runtime by the LibraryLoader. The virtual machine then runs the program with
access to these external libraries.

- Linking ensures that references to external functions are resolved at runtime.
- Loading brings those libraries into memory so that the program can use them during execution.

This is a common approach in many modern operating systems and programming environments, allowing programs
to be more modular, flexible, and memory-efficient by sharing common code in dynamically linked libraries.
