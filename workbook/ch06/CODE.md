
## Some Thoughts on Code

Code can serve a dual purpose:
- communicate ideas, and
- be executed by a machine.

Let's explore this further.


__Code is more about communication than productification__

In theory, the primary function of code is to produce behavior in a machine. But in practice,
code is as much for humans as it is for machines. It is a medium of thought, coordination, and
intent--written not just to be executed but to be read, understood, extended, and maintained by
*other* developers.
	
- Readable code is communicative code. Variables, functions, and structure must convey intent,
  not just logic. Consider two equivalent programs--one written hastily, the other thoughtfully
  named and structured. Only one invites collaboration and survives time.

- Software is never final. It lives in a context of teams, evolving requirements, and decades-long
  life cycles. Productification (turning code into a final "product") is a goal, but it's not the
  end. Maintaining, evolving, and understanding code later is only possible when the code communicates
  clearly.

- A good analogy: *Code is literature, not assembly line output.* Comments, naming, and structure
  function like grammar and style--not necessary for *execution*, but essential for *comprehension*.


__The machine doesn't care what a program is until you reach machine code__

At runtime, all high-level code—Python, C++, JavaScript, etc.—is meaningless to the CPU. Only once
it is compiled, interpreted, or JIT-compiled into machine code (binary instructions specific to an
architecture) does the computer recognise it.

- The machine cares only about its instruction set: numerical opcodes, registers, memory addresses.
  It doesn't care whether you used clean code, SOLID principles, or even wrote it in English or
  obfuscated.

- This underscores that code is dual-purpose:
	- For the machine: eventually reduced to machine code.
	- For the human: structured and expressed in a way that encodes logic, but also intent and meaning.
	- This makes programming languages human-machine boundary layers. They're not for the machine per
      se, but to help humans get to a state where they can express an idea in machine-translatable form.


__Code is communication between humans as much as machines and humans__

In practice, software development is not an isolated act between programmer and computer. It's a social
process—teams of people, distributed over time and geography, collaborate through code.

- Code is the common language of software teams. It must be structured so others can:
    - Understand what's been done
	- Debug and extend it
	- Trust its correctness
	- Just like architecture drawings in civil engineering, code is a medium for negotiation
      and collaboration, not just execution.
	- Examples:
	    - An API is a contract between teams.
	    - A pull request is an argument for change, using code to explain what and why.
	    - Comments and commit messages are narrative layers around the formalism of logic.[^comment]

This dual role—communication with machines and other humans, explains why programming is both technical
and linguistic. Writing good code is not just about getting it to work, it's about getting it to work well
in a shared human system.

| Aspect            | For Machine                | For Human Developer                  |
|-------------------|----------------------------|--------------------------------------|
| Code Content      | Must compile/interpret     | Must express intent                  |
| Structure         | Irrelevant post-compilation| Crucial for comprehension            |
| Naming/Comments   | Ignored                    | Key to communication                 |
| Purpose           | Executable behavior        | Collaborative expression of behavior |

[^comment]: I'm not sure that comments have to be inlined with code, as the parctice have been.
I would rather see separate documents, perhaps in the spirit (not the execution) as "literate
programming" (cf. Knuth). I can see a shift of this may happend in regard to the events of LLMs.
For me code is enough as it stands alone. Well, it should be well written then.

