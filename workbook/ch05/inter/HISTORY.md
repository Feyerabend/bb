
## Some History of Intermediate Code

### UNCOL

Many would probably start the history of intermediate code with UNCOL (Universal Computer Oriented Language), which is a universal
intermediate language for compilers. The idea was introduced in 1958, by a SHARE ad-hoc committee.[^1] It was never fully specified
or implemented; in many ways it was more a concept than a language.

UNCOL was intended to make compilers economically available for each new instruction set architecture and programming language.
Each machine architecture would require just one compiler back end, and each programming language would require one compiler front end.
This was a very ambitious goal because compiler technology was in its infancy, and little was standardized in computer hardware and software.

The concept of such a universal intermediate language is old: the SHARE report (1958) already says "[it has] been discussed by many
independent persons as long ago as 1954." Macrakis (1993) summarizes its fate:

> UNCOL was an ambitious effort for the early 1960s. An attempt to solve the compiler-writing problem, it ultimately failed because
> language and compiler technology were not yet mature. In the 1970s, compiler-compilers ultimately contributed to solving the problem
> that UNCOL set itself: the economical production of compilers for new languages and new machines.

UNCOL is sometimes used as a generic term for the idea of a universal intermediate language. The Architecture Neutral Distribution
Format is an example of an UNCOL in this sense, as are various bytecode systems such as UCSD Pascal's p-code, and most notably Java bytecode.[^3]


[^1]: Strong, J.; Wegstein, J.; Tritter, A.; Olsztyn, J.; Mock, O.; Steel, T. (August 1958).
"The Problem of Programming Communication with Changing Machines: A Proposed Solution".
Communications of the ACM. 1 (8): 12-18. doi:10.1145/368892.368915. Retrieved 21 February 2022.

[^3] John English, Introduction to Operating Systems: Behind the Desktop, Palgrave MacMillan 2005, ISBN 0230374085, p. 10


UNCOL, short for "Universal Computer Oriented Language," was a theoretical intermediate language proposed in the 1950s. 

Core Idea:
* *Bridge the Gap:* UNCOL aimed to simplify the process of translating various high-level programming languages into machine code for different computer architectures.
* *Two-Step Compilation:* 
    * *Front-end:* Each high-level language (like Fortran, COBOL) would have a compiler that translated it into UNCOL.
    * *Back-end:* A separate compiler would then translate the UNCOL code into machine code specific to the target computer.

Why it Was Important (in Theory):

* *Reduced Development Effort:* By creating a single intermediate representation, the number of compilers needed would be significantly reduced. Instead of N languages needing M compilers for M machines, you'd have N front-ends and M back-ends.
* *Increased Portability:* Programs could be easily adapted to run on different computers by simply using the appropriate back-end compiler.

Why it Didn't Happen (in Practice):

* *Complexity:* Designing a truly universal intermediate language that could effectively represent the nuances of different programming languages proved to be incredibly challenging.
* *Technological Limitations:* The computing power available at the time was insufficient to efficiently handle the translation process through an intermediate representation.

Impact:

* *Conceptual Foundation:* Although UNCOL itself was never fully realized, the concept of intermediate representations played a crucial role in the development of modern compilers.
* *Influence on Later Work:* Many subsequent compiler technologies, such as bytecode systems (like Java bytecode) and intermediate representations used in modern compilers, can be seen as successors to the ideas of UNCOL.

Summary:

UNCOL was a visionary concept that aimed to revolutionize compiler design. While it ultimately fell short of its ambitious goals, it laid the groundwork for many of the compiler techniques that are used today.


### References:

* Conway, Melvin E. (1 October 1958). "Proposal for an UNCOL". Communications of the ACM. 1 (10): 5-8. doi:10.1145/368924.368928. ISSN 0001-0782.
* Jean E. Sammet, Programming Languages: History and Fundamentals, Prentice-Hall, 1969. Chapter X.2: UNCOL (Significant Unimplemented Concepts), p. 708.
* SHARE Ad-Hoc Committee on Universal Languages (J. Strong, J. Olsztyn, J. Wegstein, O. Mock, A. Tritter, T. Steel), "The Problem of Programming Communication with Changing Machines", Communications of the ACM 1:8:12-18 (August 1958) and 1:9:9-15 (September 1958).
* Stavros Macrakis, "From UNCOL to ANDF: Progress in Standard Intermediate Languages", White Paper, Open Software Foundation Research Institute, RI-ANDF-TP2-1, January, 1992. Available at CiteSeer
* T.B. Steel, Jr., "UNCOL: Universal Computer Oriented Language Revisited", Datamation (Jan/Feb 1960), p. 18.
* T.B. Steel, Jr., "A First Version of UNCOL", Proc. Western Joint Computer Conference 19:371 (Los Angeles, May 9-11, 1961).
* T.B. Steel, Jr., "UNCOL: The Myth and the Fact", Annual Review in Automatic Programming 2:325 (1961).
