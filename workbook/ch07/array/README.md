
## Array Computing

Array computing has its roots in early vector and parallel processing machines,
evolving into modern-day architectures where even small processors and specialised
chips leverage array operations for efficiency. The journey begins with early array
processors, such as the ILLIAC IV in the 1970s, which introduced the concept of
executing the same operation on multiple data points simultaneously, a key principle
in SIMD (Single Instruction, Multiple Data) computing. These machines were designed
for scientific and engineering applications, where large datasets required rapid
processing.

As computing advanced, supercomputers like the Cray-1 embraced vector processing,
optimising performance by executing mathematical operations on entire arrays rather
than processing individual numbers sequentially. This idea extended into general-purpose
processors, where instruction sets started including vectored operations, such
as Intel's MMX and SSE extensions or ARM's NEON. These instructions allowed CPUs
to perform multiple arithmetic calculations in a single step, accelerating tasks
like graphics processing, cryptography, and machine learning.

With the rise of GPUs, array computing took a new form in the 2000s. Originally
designed for graphics, GPUs inherently operated on large data arrays (pixels, vertices)
and evolved into general-purpose accelerators (GPGPU computing). NVIDIA's CUDA and
OpenCL frameworks enabled developers to harness GPUs for tasks traditionally handled
by CPUs, vastly improving performance in fields like AI, physics simulations, and
scientific computing.

Modern processors, even in mobile devices, integrate array computing principles.
AI-focused accelerators like Google's TPU, Apple's Neural Engine, and AMD's CDNA
use specialised matrix multiplication units to efficiently perform deep learning
tasks. RISC-V and other emerging architectures continue to incorporate SIMD and
parallel processing instructions, ensuring that array computing remains a fundamental
part of both high-performance and embedded computing. The shift towards domain-specific
accelerators further emphasises the growing reliance on array-based processing,
making it a cornerstone of contemporary computational efficiency.


### ILLIAC IV

ILLIAC IV was one of the earliest attempts at massively parallel computing, designed
in the late 1960s and completed in the early 1970s. It was developed by the University
of Illinois in collaboration with DARPA and Burroughs Corporation. The machine was
intended to be a breakthrough in high-speed computing by implementing SIMD (Single
Instruction, Multiple Data) processing, meaning that a single instruction could be
executed across multiple data elements simultaneously.

The design of ILLIAC IV was heavily influenced by the idea of using an array of
processors working in parallel. It was initially planned to have 256 processing
elements, but due to budget constraints and technical difficulties, only 64
processors were implemented. Each processor could perform arithmetic and logical
operations on its own set of data, while a central control unit issued instructions
to all processors simultaneously. This approach made the machine highly efficient
for applications that required extensive numerical calculations, such as fluid
dynamics, weather modelling, and simulations.

Despite its ambitious design, ILLIAC IV faced significant delays and challenges.
Fabrication and integration issues slowed down its development, and by the time
it became operational in 1975, other computing technologies had advanced
significantly. Additionally, security concerns led to the system being installed
at NASA Ames Research Center instead of the University of Illinois. The machine's
architecture was highly specialised and not well-suited for general-purpose
computing, which limited its wider adoption.

Although ILLIAC IV did not achieve its full potential, it played a critical role
in advancing parallel computing concepts. Its failure to meet initial expectations
was offset by the influence it had on later developments in high-performance
computing. The lessons learned from ILLIAC IV contributed to the evolution of
vector processors in supercomputers like the Cray-1 and laid the foundation for
modern parallel processing architectures, including GPUs and SIMD instructions
found in today's CPUs. The project demonstrated both the potential and the
challenges of large-scale parallel computing, shaping future research in
efficient data processing techniques.

- https://en.wikipedia.org/wiki/Array_programming

### APLE: Array Programming Language Extension

Rather than serving as a robust starting point for a larger project, the
implementation "aple.py" is intended as a conceptual exploration of extending
the widely used Python library, NumPy. The focus is not on building a comprehensive
or production-ready system but rather on deepening the understanding of array
computing principles. This serves as an educational exercise rather than a
foundation for developing a full-fledged compiler or interpreter for an
array-oriented language.

Many ideas mangled by LLM comes from: https://github.com/rodrigogiraoserrao/RGSPL.

> [!IMPORTANT]
> You must install the NumPy library for Python to get `APLAarray` to work.
