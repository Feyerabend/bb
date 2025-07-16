
## Reference

Some folders may occasionally contain a REFERENCE.md file, indicating a link between the
physical book and this repository. Given the changing nature of online resources and the
ongoing discovery of new material, I've chosen to publish the book's bibliography here
rather than include it directly in the print version.


## Documents

Folders may contain documents in the Microsoft ".docx" format (or PDF). These are generated
directly by Gemini Deep Research. They are heavily referenced and can serve as a starting
point for further exploration or guidance on the topics.


## Audio Discussions

With the assistance of Google’s NotebookLM, a series of WAVE files has been produced.
Each episode can be downloaded individually, and you'll need a suitable audio player
to listen to them.

Also some are Gemini-generated Audio Overview in MP3 format.


## Code

These folders contain the complete code for the book's examples, save for cases where the
book itself exhausts the need. In such instances, the printed code suffices, and repetition serves
no further end. The workbook, on occasion, takes the liberty of expanding upon the book's
proposals, extending its reach beyond their immediate intent. Where the book offers a scaffold,
the workbook sometimes builds, at times extrapolates, and at others, diverges.

The book seeks to deepen your grasp of computation and programming, often through direct
engagement with code as a starting point. Code is not merely demonstration but inquiry, and the
workbook, in kind, takes the liberty of pursuing a line where the book may leave off.
The endeavour is not to repeat but to reveal, to press on where the book gestures, making
explicit what is left implicit and raising questions where none yet stand.

The code examples in this book are written in standard Python (version 3), ANSI C, MicroPython
for the Raspberry Pi Pico, and sometimes JavaScript compatible with most modern web browsers.
To help readers grasp core programming principles, dependencies have been kept to a minimum.
Except where necessary--such as for specialised hardware interfaces like an LCD driver--no
external libraries are used, or at least kept to a minimum. This approach encourages a focus
on foundational coding concepts without reliance on third-party libraries.


### Libraries

Contrary to common recommendations today, writing code for widely used algorithms instead
of relying on external (third party) libraries can benefit learners by building familiarity
with fundamental techniques and reducing external dependencies. For instance, this book
suggests writing a simple *virtual machine* to allow code to abstract cleanly from underlying
systems.

While external libraries that are standard, robust, and well-tested should generally be used,
avoid relying on small, non-essential libraries that add little value to the core task and
may introduce unnecessary dependencies.

In the real world, it's worth noting that writing custom solutions for everything can
sometimes 'reinvent the wheel' and increase development time, especially for common tasks
where libraries are standardised, robust, and highly optimised. Established libraries also
tend to be well-documented and peer-reviewed, meaning they've been vetted for reliability
and bugs. The right balance often means selectively using trusted, essential
libraries--especially for complex tasks that are beyond the immediate scope of this
book--while still tackle more straightforward implementations.


## Projects

The purpose of these folders containing project suggestions is to facilitate a deep
and engaging exploration of computing, programming and some computer science concepts.
By leveraging the guidance provided by large language models (LLMs), you can dive
into a wide range of topics and build a personalised understanding of complex subjects.
When you encounter a concept or topic that isn't immediately clear, these resources
encourage you to explore it more thoroughly, gradually enhancing both your knowledge
and problem-solving abilities. This process empowers you to develop a foundational
understanding that grows organically from initial guidance to independent mastery.

The project suggestions span a range of difficulty levels, from introductory to
advanced. Depending on your experience, the time required to complete each project
may vary significantly. The final output can also vary based on your goals--whether
you opt for a comprehensive report or a straightforward description of the code's
functionality. While LLMs provide considerable support, truly internalising your
learning may call for unique approaches or creative problem-solving methods to
solidify your understanding.

For example, working in a group enables you to collaborate not only in coding but
also in reviewing each other's work. This collaboration can enhance both the quality
of the code and your understanding of the concepts, as discussing and evaluating
different approaches often reveals new insights and clarifies complex ideas.

A teacher can use LLMs effectively to both support and assess students' learning
in various ways. Here's how:

1. *Personalised guidance*: Teachers can set up LLM-guided tasks that allow students
   to explore topics individually, adjusting the level of guidance based on each
   student's progress. By assigning projects that require iterative improvement,
   teachers can assess students' ability to independently deepen their understanding,
   even as they rely on LLMs for initial support.

2. *Evaluating problem-solving process*: Teachers can ask students to document
   their problem-solving journey, including questions they asked the LLM,
   insights gained, and adjustments made based on feedback. This documentation
   can show not only what the student learned but also how they approached challenges,
   offering teachers insight into the student's development and problem-solving skills.

3. *Code review and reflection exercises*: Teachers can encourage students to review
   code produced by others or the LLM itself, evaluating both the quality of code
   and their understanding. These reviews can be assessed on students' ability to
   critique effectively, spot potential issues, and suggest improvements, which can
   be telling of their grasp on the material.

4. *Project-based evaluation*: Teachers can design (or redisng) projects where students
   are graded on both their final product and the insights they share about their
   process. This can include decisions on code structure, optimisations, or even
   explanations of what the code does and why. The LLM can serve as a coding assistant,
   but students will need to demonstrate deeper understanding by articulating
   *the reasoning behind* their choices.

5. *Peer collaboration and reflection*: Teachers can encourage group work where students
   use the LLM collaboratively, asking them to reflect on what insights came from each
   team member versus the LLM. Evaluating these reflections can reveal how well students
   can integrate and synthesise information from different sources, including AI tools
   and peer discussions.


By using LLMs as part of the teaching and evaluation process, teachers can assess not
only the end result but also students' problem-solving processes, engagement with the
material, and ability to work both independently and collaboratively.


## Management

When using LLMs as part of the learning environment, teachers should take an adaptive approach,
tailoring project assignments based on each student's prior knowledge and skills. The goal is to find
a balance where projects are neither too simple nor too advanced, offering enough challenge to foster
growth without causing frustration or disengagement. This type of project-based guidance diverges
from traditional instruction that relies heavily on standardised exercises or uniform tests.

In this model, teachers act more as *mentors*, setting up projects that encourage critical thinking,
creativity, and independent learning. Rather than simply assessing students' ability to memorise facts
or solve pre-defined problems, the emphasis shifts toward evaluating how well students can apply
their knowledge to real-world scenarios, often with open-ended solutions. This encourages students
to explore topics more deeply, experiment with different approaches, and develop unique solutions,
all with the support of LLMs as interactive resources rather than mere answer-providers.

Through this adaptive project management, teachers can observe and assess students' problem-solving
skills, persistence, and ability to integrate new information. This approach also provides a richer, more
individualised learning experience for students, as they can leverage LLMs to clarify concepts, brainstorm
ideas, and seek guidance on specific questions, all tailored to the level of complexity that best suits
their current stage of learning.
