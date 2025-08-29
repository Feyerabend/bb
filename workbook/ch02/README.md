
__Printed book reference: see explanations and examples in [BOOK].__

* [VM1](./vm1/)     - Simple stack.based machine
* [REGVM](./regvm/) - Simple register-based machine
* [VM2](./vm2/)     - "Forth" inspired machine
* [VM3](./vm3/)     - Enchanced with jump instructions, comparison
                      operators, memory storage, loops, conditionals,
                      and function calls (activation records, frame pointers)
* [MEM](./mem/)     - Memory management in blocks
* [VM4](./vm4/)     - Data stack and frame stack, call/return

## Exploring the virtual machine landscape

This chapter emphasises the concept of 'machines' as a foundation for abstract reasoning, particularly
in the context of virtual machines (VMs). Virtual machines serve as a conceptual and practical bridge,
enabling us to model and understand the behaviour of programming languages. By studying virtual machines,
one can explore both the specific implementations of various programming paradigms—such as functional,
object-oriented, or imperative languages—and the architectural differences in how these machines are
designed and constructed.

In this context, a virtual machine is understood primarily as a model for implementing and interpreting
programming languages. This allows us to delve into the essence of computing as a software-building
activity, where the machine is not just a physical entity but also an abstract computational model.
From this perspective, the focus shifts to how software interfaces with and shapes the underlying
computational logic. In contrast, other approaches, such as those rooted in hardware engineering,
might prioritise a bottom-up view, starting with the physical properties of circuits and processors.

A pivotal example for students to study is the 'von Neumann machine,' which serves as the archetype
for most real-world computers today. This model, based on the principles of stored-program architecture,
highlights the interplay between memory, processing, and instruction flow. Understanding the von Neumann
architecture provides a foundational lens for grasping the limitations and possibilities inherent in most
modern computing systems. Optionally comparing this with alternative architectures, such as the Harvard
architecture or parallel processing machines, further broadens the understanding of how virtual machines
can diverge based on their design goals. We do not however go into details on those approaches here,
but remains open for further explorations.

By engaging with these concepts, students of computers and programming can gain a richer appreciation
of how virtual machines embody different paradigms, allowing us to reason about programming languages
and computation more broadly. This exploration serves not only to deepen understanding of specific
programming models but also thus to illuminate the broader landscape of computational theory and practice.

The connection between programming language virtual machines (VMs) and a simple AI model like the
Perceptron lies in their shared foundation of abstraction and computation. Virtual machines abstract
away the complexities of hardware, providing a platform-independent environment for executing high-level
code. Similarly, the Perceptron--one of the earliest forms of artificial neural networks--encapsulates
learning and decision-making in a mathematical model. Both systems use layers of abstraction to simplify
complex tasks, whether by enabling code execution across different architectures or by recognising
patterns in data. In this sense, both VMs and AI models serve as conceptual frameworks for understanding
computation and learning in different domains.

Moreover, both VMs and the Perceptron operate on the principle of transforming inputs into outputs
through well-defined processes. In a VM, this involves interpreting or compiling code and executing
instructions, while in the Perceptron, it involves computing weighted sums of inputs and applying
activation functions to produce predictions. This parallel highlights how computational models, whether
for running software or simulating intelligence, are built on structured, rule-based systems that process
information systematically. The inclusion of the Perceptron in the folder underscores the idea that
programming and AI are deeply interconnected, as both fields rely on creating and manipulating abstract
models to solve real-world problems.

In the early days of digital computing, the von Neumann and Harvard architectures represented two distinct
approaches to computer design. The von Neumann architecture, proposed by John von Neumann in 1945, used a
single memory for both instructions and data, allowing for flexible programming but also introducing the
risk of the "von Neumann bottleneck" due to shared memory access. In contrast, the Harvard architecture,
originally used in early relay-based computers like the *Harvard Mark I*, separated memory for instructions
and data, enabling simultaneous access and improving speed but making programming and memory management
more rigid. Over time, modern processors have incorporated elements of both architectures to optimise
performance and flexibility.
