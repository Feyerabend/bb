
## History of BASIC

*BASIC* (Beginner's All-purpose Symbolic Instruction Code) was created in 1964 at Dartmouth College
by John G. Kemeny and Thomas E. Kurtz. Their mission was to make computing accessible to students and
non-specialists, particularly in an educational context. At the time, programming required expertise
in languages like Fortran or COBOL and access to batch-processing systems with punch cards. BASIC,
designed for time-sharing systems, allowed interactive programming with immediate feedback, a radical
shift that aligned with its pedagogical goal of teaching problem-solving through coding.

The original Dartmouth BASIC was simple, with commands like `PRINT`, `LET`, `IF...THEN`, and `GOTO`.
Its English-like syntax and minimalistic design made it an ideal teaching tool. Distributed freely,
it was adopted by other institutions, setting the stage for its widespread use.


### Pedagogical Value

BASIC's design was rooted in education, and its pedagogical impact was profound:

- *Lowering Barriers*: BASIC's intuitive syntax allowed students with no prior computing experience
  to write programs quickly. Commands like `INPUT` and `PRINT` mirrored natural language, making
  abstract concepts like variables and loops tangible.

- *Immediate Feedback*: Running a program line-by-line in an interactive environment helped learners
  see cause-and-effect relationships, reinforcing debugging and logical thinking skills.

- *Encouraging Exploration*: BASIC's simplicity enabled students to experiment, fostering creativity.
  For example, writing a program to print patterns or calculate grades gave students a sense of
  ownership over technology.

- *Democratising Computing*: By teaching BASIC in schools and colleges, educators empowered non-STEM
  students to engage with computers, broadening participation in an era when computing was elitist.

- *Foundation for Computational Thinking*: BASIC introduced core programming concepts (variables,
  conditionals, loops) in a forgiving environment, preparing students for more complex languages.

In the 1970s and 1980s, BASIC's role in education expanded as microcomputers entered classrooms and homes.
Books like *BASIC Computer Games* (1978)--yes I have one still--and magazines like *Creative Computing*
provided engaging exercises, turning learning into a playful, self-directed activity. This approach
influenced modern educational tools like Scratch, which prioritise interactive learning.


### Rise on Microcomputers

BASIC's popularity surged in the 1970s and 1980s with the microcomputer revolution. Its low resource
requirements (minimally fitting in just 4KB of RAM) and simplicity made it perfect for early personal
computers. Naturally it could be expanded with more features. Developments include:

- *1975: Altair BASIC*: Developed by Bill Gates and Paul Allen for the Altair 8800, this was
  Microsoft's first product. Distributed on paper tape, it brought programming to hobbyists.[^code]

- *Home Computers*: Manufacturers embedded BASIC interpreters in ROM, making it the default interface
  for machines like the Commodore 64, Apple II, Atari 400/800, and Sinclair ZX Spectrum. Users could
  boot directly into BASIC, encouraging experimentation.
  - *Commodore BASIC* (1977) powered the PET and Commodore 64, widely used in homes and schools.
  - *Applesoft BASIC* (1978), written by Microsoft for the Apple II, added graphics and floating-point math.
  - *Sinclair BASIC* (1980) was optimized for the ZX80 and ZX Spectrum's limited memory.

- *Cultural Impact*: BASIC's accessibility democratised programming. Students, hobbyists, and children
wrote games, utilities, and educational tools, fostering a DIY programming culture. Publications like
*Compute!* shared BASIC listings, amplifying its reach.

BASIC became synonymous with personal computing, particularly in education, where it was a staple in
computer literacy curricula.

[^code]: A released source version can be found at: https://www.gatesnotes.com/microsoft-original-source-code.


### Dialects of BASIC

BASIC's open design led to numerous dialects, each adapted to specific platforms or purposes. Examples include:

1. *Dartmouth BASIC* (1964)
   - Features: Basic commands (`PRINT`, `INPUT`, `GOTO`), line numbers, educational focus.
   - Example:
     ```basic
     10 PRINT "Hello, World!"
     20 END
     ```

2. *Altair BASIC* (1975)
   - Features: Compact, supporting arithmetic and strings.
   - Example:
     ```basic
     10 LET A = 5
     20 PRINT A * 2
     30 END
     ```

3. *Tiny BASIC* (1976)
   - Features: Extremely minimal interpreter designed for
     microcomputers with as little as 2 KB of RAM.
   - Example:
    ```basic
    10 LET A = 3
    20 LET B = A + A
    30 PRINT B
    40 END
    ```

4. *Applesoft BASIC* (1978)
   - Features: Floating-point math, graphics (`HPLOT`).
   - Example:
     ```basic
     10 HGR
     20 HCOLOR=3
     30 HPLOT 100,100
     40 END
     ```

5. *Commodore BASIC* (1977–1982)
   - Features: `PEEK` and `POKE` for memory manipulation.
   - Example:
     ```basic
     10 POKE 53280,0
     20 PRINT "Black Border"
     30 END
     ```

6. *Sinclair BASIC* (1980)
   - Features: Single-key entry, optimised for low memory.
   - Example:
     ```basic
     10 PRINT AT 10,10;"Hello"
     20 PAUSE 50
     30 CLS
     40 END
     ```

7. *Microsoft BASIC* (1976–1980s)
   - Features: Portable across platforms (e.g., TRS-80, IBM PC).
   - Example:
     ```basic
     10 INPUT "Enter a number: ", N
     20 PRINT N * N
     30 END
     ```

8. *QuickBASIC/QBASIC* (1985/1991)
   - Features: Structured programming, IDE.
   - Example:
     ```basic
     CLS
     INPUT "Enter your name: ", name$
     PRINT "Hello, "; name$
     END
     ```

9. *Visual Basic* (1991)
   - Features: GUI design, event-driven programming.
   - Example:
     ```basic
     Private Sub Command1_Click()
         MsgBox "Hello, World!"
     End Sub
     ```

### Decline of BASIC

BASIC's dominance faded in the late 1980s and 1990s due to technical, cultural, and pedagogical factors:

- *Performance*: Interpreted BASIC was slow compared to compiled languages like C or Pascal, limiting
  its use for complex applications.

- *Unstructured Code*: Early BASIC's reliance on `GOTO` produced "spaghetti code," criticised for being
  unmaintainable. Structured dialects like QuickBASIC mitigated this, but the stigma persisted.

- *Professionalization*: As software development formalised, languages with strong typing and modularity
  (e.g., C++) during the late 80 became industry standards, marginalising BASIC's beginner-focused design.

- *Hardware Advances*: Powerful PCs and GUI-based operating systems (e.g., Windows) reduced the need for
  lightweight languages. Visual Basic thrived briefly for rapid application development but was later
  eclipsed by .NET and C#.

- *Educational Shift*: BASIC faced criticism in academia for encouraging bad habits. In 1975, Edsger
  Dijkstra famously critiqued BASIC, stating it "cripples the mind" by allowing unstructured programming,
  potentially hindering students' ability to learn disciplined coding practices. This view gained
  traction as educators favored languages like Pascal, which emphasised structure.

[^cripple]: Dijkstra, E. W. (1975). EWD498: *How do we tell truths that might hurt?*
Archived by the University of Texas:
https://www.cs.utexas.edu/users/EWD/ewd04xx/EWD498.PDF

By the 2000s, BASIC was a niche language, though Visual Basic and open-source projects like FreeBASIC
persisted. Its educational role diminished as Python and visual tools like Scratch took over.


### Criticisms of BASIC

BASIC faced significant criticism, particularly from academics and professional programmers:

- *Unstructured Programming*: The heavy use of `GOTO` led to convoluted code, making it hard to teach
  modular design. Critics argued this instilled poor habits in beginners, complicating transitions to
  languages like C or Pascal.

- *Oversimplification*: BASIC's simplicity, while pedagogically valuable, was seen as a double-edged
  sword. It shielded learners from low-level concepts like memory management, leaving them unprepared
  for systems programming.

- *Lack of Standardization*: The proliferation of dialects created inconsistencies, frustrating learners
  who moved between platforms (e.g., Commodore BASIC's `POKE` vs. Applesoft's `HPLOT`).

- *Perceived Amateurism*: BASIC's association with hobbyists and "toy" programs led to a perception that
  it was not serious, alienating it from professional and academic circles.

- *Pedagogical Harm*: Dijkstra and others argued that BASIC's leniency (e.g., no type declarations)
  fostered sloppy thinking, potentially limiting students' ability to grasp rigorous programming principles.

Despite these critiques, defenders noted that BASIC's accessibility sparked interest in computing for
millions, and structured dialects like QuickBASIC addressed some concerns. The debate reflects a tension
between ease of learning and preparation for advanced programming.


### Lessons from BASIC

BASIC's history offers valuable insights, particularly in pedagogy and language design:

1. *Pedagogical Power of Simplicity*: BASIC's success in education stemmed from its low entry barrier,
   showing that beginner-friendly tools can inspire lifelong interest in computing. Modern tools like
   Python and Scratch build on this legacy.

2. *Balancing Simplicity and Structure*: BASIC's unstructured nature was both a strength (easy to learn)
   and a weakness (hard to scale). This highlights the need for languages to evolve with learners, as
   seen in QuickBASIC's structured features.

3. *Ecosystem Drives Adoption*: BASIC's integration into microcomputers made it ubiquitous, underscoring
   the importance of accessibility and distribution in educational tools.

4. *Criticism Informs Progress*: The backlash against BASIC spurred improvements in programming education,
  leading to languages like Pascal and Python that balance simplicity with discipline.

5. *Cultural Legacy*: BASIC's role in fostering a DIY programming culture shows how tools shape communities.
   Its decline reflects the challenge of staying relevant amid technological shifts.

6. *Pedagogical Evolution*: BASIC's immediate feedback and interactivity remain gold standards in teaching.
   However, its criticisms emphasize the need for tools that transition learners to advanced concepts without
   sacrificing engagement.


### Conclusion

BASIC was a cornerstone of the microcomputer era, transforming computing from an elite discipline to a tool
for all. Its pedagogical value—rooted in simplicity, interactivity, and accessibility—made it a gateway for
millions to learn programming, shaping the tech industry and educational practices. However, criticisms of
its unstructured design and perceived limitations highlight the challenges of balancing beginner-friendliness
with rigour. BASIC's rise and fall illustrate the power of accessible tools and the need for evolution in
response to changing needs. Its legacy endures in modern educational languages and the ethos of democratising
technology.

