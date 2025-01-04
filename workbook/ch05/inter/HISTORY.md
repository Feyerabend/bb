## Some History of Intermediate Code

### UNCOL: Universal Computer Oriented Language

The concept of intermediate code, specifically the idea of a universal intermediate language, can trace its origins back to UNCOL (Universal Computer Oriented Language), which was proposed in 1958 by a SHARE ad-hoc committee. UNCOL was a theoretical design aimed at simplifying the compilation process across different machine architectures and high-level programming languages. While it was never fully implemented, its influence on the development of compilers and intermediate representations has had a lasting impact.

### Core Idea of UNCOL

UNCOL was envisioned as a universal intermediate language that would bridge the gap between high-level programming languages and machine code. The idea was based on the principle of two-step compilation:
1. Front-End: Each high-level programming language (e.g. Fortran, COBOL) would have a compiler that translated the source code into UNCOL.
2. Back-End: A separate compiler would then take this UNCOL code and translate it into the machine code specific to the target computer architecture.

This two-phase approach meant that, theoretically, fewer compilers would be needed. Instead of requiring multiple compilers for each language and each machine, there would only need to be one compiler front-end for each language and one back-end for each machine architecture, which significantly reduced development effort.

Why It Was Important (in Theory)

The promise of UNCOL was substantial:
- Reduced Development Effort: By centralizing the translation into an intermediate format, fewer compilers would be needed. This could potentially streamline the development of compilers for both new languages and new machine architectures.
- Increased Portability: Programs written in any high-level language could, in theory, be easily ported to different computer systems by simply using a different back-end compiler, enabling easier cross-platform execution.

Why It Didn't Happen (in Practice)

Despite its ambitious goals, UNCOL faced numerous challenges:
- Complexity: The task of designing a universal intermediate language capable of representing the nuances of many different programming languages proved to be far more difficult than anticipated. Each programming language has unique features, making it tough to standardize their representation in a single language.
- Technological Limitations: The computing power available at the time was not sufficient to handle the complexities of converting high-level code into an intermediate representation, and then translating that into machine code efficiently. Compiler technology was still in its early stages, and many aspects of machine and language design were still evolving.

Impact on Modern Compiler Design

Although UNCOL itself was never fully realized, its legacy is seen in the intermediate representations used in modern compilers. UNCOL laid the groundwork for the development of bytecode systems (such as UCSD Pascal's p-code and Java bytecode) and modern intermediate representations used to compile high-level languages to machine code for various architectures. These modern systems, such as the Architecture Neutral Distribution Format (ANDF), are direct descendants of the ideas proposed by UNCOL.

For instance, Java's bytecode, which is designed to run on the Java Virtual Machine (JVM), follows a similar idea of a universal intermediate representation that can be executed on any system that supports the JVM, similar to the vision of UNCOL.

### Conclusion

In summary, while UNCOL did not achieve its goal of becoming the universal intermediate language, it played a significant conceptual role in the development of compiler theory. The idea of using an intermediate language to bridge the gap between high-level languages and machine code remains a cornerstone of modern compiler design.

#### References:
1.	Conway, M. E. (1958). Proposal for an UNCOL. Communications of the ACM, 1(10), 5-8. doi:10.1145/368924.368928
2.	Sammet, J. E. (1969). Programming Languages: History and Fundamentals, Prentice-Hall. Chapter X.2: UNCOL (Significant Unimplemented Concepts), p. 708.
3.	Macrakis, S. (1993). From UNCOL to ANDF: Progress in Standard Intermediate Languages, Open Software Foundation Research Institute, RI-ANDF-TP2-1.
4.	Steel, T. B., Jr. (1960). UNCOL: Universal Computer Oriented Language Revisited, Datamation, Jan/Feb. p. 18.


---

### Pascal P-Code

Pascal P-Code (Portable Code) is an intermediate code used by the UCSD (University of California, San Diego) Pascal system in the 1970s. It was a design aimed at improving the portability of Pascal programs across different machine architectures. The concept behind P-code was to have a virtual machine that could execute an intermediate language, allowing Pascal programs to be compiled once into P-code, and then run on any machine with a suitable interpreter. This represented a key step in the evolution of language portability and compiler design.

Origins and Purpose of Pascal P-Code

Pascal P-code was developed as part of the UCSD Pascal system, which was designed to provide a simple and efficient compiler for the Pascal programming language, particularly in an educational context. The P-code itself is a set of machine-independent instructions that an interpreter could execute. Instead of generating machine-specific code directly from the Pascal source, the UCSD Pascal compiler would generate P-code, which could then be executed by the P-code interpreter on various platforms.

The P-code thus acted as an intermediate representation, serving as a "universal" code between the high-level Pascal source and the machine-specific machine code. This design allowed Pascal programs to be ported to any platform with a suitable P-code interpreter, vastly increasing the portability of Pascal applications compared to directly compiled machine code.

Features of Pascal P-Code

1. Portability: One of the primary advantages of P-code was that it allowed a single compiled form of a program to be executed on various platforms. Unlike traditional compilation that generated platform-specific machine code, P-code was designed to be interpreted on any machine that had a P-code interpreter, which could be relatively easily written for different architectures.
2. Virtual Machine: The P-code system used a virtual machine (PVM) to execute the P-code instructions. This approach is similar to the concept behind modern virtual machines used in systems like Java, which compiles source code into bytecode that is then executed by the Java Virtual Machine (JVM).
3. Optimisation: While P-code was machine-independent, it still allowed some level of optimisation. The UCSD Pascal system would perform optimisations on the P-code itself before it was interpreted, improving the efficiency of execution on different hardware platforms.

Influence on Modern Systems

Pascal P-code was a precursor to modern bytecode systems, such as Java bytecode. Just as Java programs are compiled into bytecode and executed on the Java Virtual Machine (JVM), Pascal programs compiled into P-code could be interpreted and run on any platform with a P-code interpreter. This idea of an intermediate representation for portability would later become fundamental to many programming languages and systems, including the development of Java in the mid-1990s.

Challenges and Limitations

1. Performance: While P-code provided portability, the performance was often slower than directly compiled machine code because the P-code had to be interpreted by a virtual machine. The interpreter added an overhead, meaning that P-code execution was not as efficient as native machine code.
2. Complexity: The use of an additional layer (the P-code interpreter) introduced complexity in both the compilation process and the execution environment. This required more resources, including memory and processing power, to run programs compared to native code compilation.
3. Obsolescence: As hardware became more standardised and compilers became more efficient, the need for an intermediate representation like P-code declined. Other systems, such as Java's bytecode and Microsoft's Common Intermediate Language (CIL), in a way eventually took its place for many applications.

Legacy

Despite these challenges, Pascal P-code was an important milestone in the development of cross-platform programming. It directly influenced the development of other intermediate representations, especially bytecode. The UCSD Pascal system's P-code provided a glimpse of the advantages and drawbacks of virtual machines and bytecode systems, concepts that would become central in later programming environments.

#### References
	
1. Wirth, N. (1976). Pascal—A programming language. Prentice-Hall.
2. University of California, San Diego. (1970s). UCSD Pascal system. Retrieved from http://www.ucsd.edu
3. Schildt, H. (2011). Java: The complete reference (8th ed.). McGraw-Hill.

For further details on the impact of Pascal P-code and its role in the evolution of modern virtual machines, you may want to consult specific works on the history of programming languages or compiler design, such as Wirth's original texts or papers on the UCSD Pascal system.

---

### Java

..

---

### LLVM

..

