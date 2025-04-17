
# Teacher's Manual: Project-First with AI-Supported Exploration
*A Comprehensive Guide for Active, Iterative, and Theory-Embedded Learning*

## Table of Contents

1. [Introduction and Vision](#1-introduction-and-vision)
2. [Philosophical Foundations](#2-philosophical-foundations)
3. [Implementation Framework](#3-implementation-framework)
   - [Course Structure](#course-structure)
   - [Lesson Structure](#lesson-structure)
   - [Role of AI](#role-of-ai)
   - [Instructor Responsibilities](#instructor-responsibilities)
4. [Creating Effective Learning Materials](#4-creating-effective-learning-materials)
   - [Designing Starter Code](#designing-starter-code)
   - [Crafting Meaningful Challenges](#crafting-meaningful-challenges)
   - [Connecting to Theory](#connecting-to-theory)
5. [Assessment & Feedback](#5-assessment--feedback)
   - [Process-Oriented Rubrics](#process-oriented-rubrics)
   - [Portfolio Assessment](#portfolio-assessment)
   - [Reflection Prompts](#reflection-prompts)
6. [Example Modules](#6-example-modules)
   - [Module 1: Algorithmic Thinking](#module-1-algorithmic-thinking)
   - [Module 2: Data Structures](#module-2-data-structures)
   - [Module 3: Systems Programming](#module-3-systems-programming)
   - [Module 4: Software Engineering](#module-4-software-engineering)
7. [Facilitating Collaborative Learning](#7-facilitating-collaborative-learning)
   - [Pair Programming Strategies](#pair-programming-strategies)
   - [Group Reflection Techniques](#group-reflection-techniques)
   - [Building a Learning Community](#building-a-learning-community)
8. [Troubleshooting & FAQs](#8-troubleshooting--faqs)
9. [Resources and Tools](#9-resources-and-tools)
   - [Technical Resources](#technical-resources)
   - [Pedagogical Resources](#pedagogical-resources)
   - [AI Tools and Guidelines](#ai-tools-and-guidelines)
10. [Further Reading](#10-further-reading)

## 1. Introduction and Vision

This manual guides instructors in implementing a project-first, AI-supported approach to computer science education. Unlike traditional methods that begin with abstract theory, our approach immerses students in realistic programming tasks from day one, using AI as a thinking partner rather than a content delivery mechanism.

### Target Audience

This approach is designed for students who:
- Already possess foundational knowledge of Python, C, JavaScript
- Understand key CS concepts like variables, loops, functions, recursion, memory management, and basic data structures
- Are ready to move beyond syntax learning to system building and deeper conceptual understanding

### Expected Outcomes

Students who experience this approach will:
- Develop confidence in modifying and extending existing codebases
- Learn to use AI as a collaborative tool rather than a crutch
- Build a deeper, context-rich understanding of computer science theory
- Acquire practical debugging, optimisation, and refactoring skills
- Gain experience with real-world software engineering practices

## 2. Philosophical Foundations

### Core Principles

#### 1. Learning Through Modification
- *Rationale*: Professional developers rarely start from scratch; they modify, extend, and refactor existing systems.
- *Implementation*: Provide working but imperfect systems as starting points.
- *Benefit*: Reduces cognitive load while maintaining authentic complexity.

#### 2. Theory Follows Practice
- *Rationale*: Abstract concepts are more meaningful when encountered in context of real problems.
- *Implementation*: Introduce theoretical concepts precisely when students need them to overcome practical challenges.
- *Benefit*: Increases motivation and retention through just-in-time learning.

#### 3. AI as a Thinking Partner
- *Rationale*: Modern developers work alongside AI tools; students should learn to use them effectively.
- *Implementation*: Guide students to use AI for debugging, exploration, and learning—not solution generation.
- *Benefit*: Builds critical thinking and AI literacy simultaneously.

#### 4. Embrace Productive Struggle
- *Rationale*: Learning happens most deeply at the edge of current understanding.
- *Implementation*: Design challenges that push students beyond comfort but remain achievable.
- *Benefit*: Develops resilience and metacognitive skills essential for lifelong learning.

#### 5. Iteration as Core Practice
- *Rationale*: Quality software emerges through repeated refinement, not perfect first attempts.
- *Implementation*: Build multiple revision cycles into projects and assessments.
- *Benefit*: Normalises experimentation and continuous improvement.

### Educational Theory Foundations

This approach synthesizes several established educational theories:
- *Constructionism* (Papert): Learning through creating and modifying meaningful artefacts
- *Zone of Proximal Development* (Vygotsky): Scaffolding learning just beyond current ability
- *Experiential Learning Cycle* (Kolb): Experience → Reflection → Conceptualisation → Experimentation
- *Cognitive Apprenticeship*: Modelling expert thinking processes in authentic contexts

## 3. Implementation Framework

### Course Structure

A typical semester-long course using this approach might follow this progression:

1. *Foundation* (Weeks 1-3)
   - Modify simple algorithms and data structures
   - Learn effective AI collaboration techniques
   - Build comfort with the iterative development process

2. *Application* (Weeks 4-10)
   - Work with increasingly complex systems
   - Integrate multiple concepts in each project
   - Deepen theoretical understanding through applied challenges

3. *Synthesis* (Weeks 11-15)
   - Tackle open-ended challenges
   - Extend projects across multiple domains
   - Reflect on learning journey and CS fundamentals

### Lesson Structure

#### 1. Launch (10-15 minutes)
- Present a runnable but limited system
- Demonstrate its current functionality and limitations
- Pose a clear challenge or extension task
- Connect to broader CS concepts

#### 2. Exploration (30-60 minutes)
- Students work individually or in pairs to modify the system
- Instructor circulates, asking probing questions rather than giving solutions
- Strategic AI use is encouraged with clear guidelines
- Mini-interventions as needed for common issues

#### 3. Reflection (15-20 minutes)
- Group discussion of approaches and challenges
- Compare different solutions and their trade-offs
- Introduce relevant theory to contextualise experiences
- Connect to professional practice and real-world systems

#### 4. Extension (In-class or homework)
- Students refine their solutions based on new insights
- Documentation of process and decision-making
- Optional challenges for advanced students
- Preparation for the next session

### Role of AI

#### Appropriate AI Uses
- *Debugging assistance*: "Why might my recursive function be causing a stack overflow?"
- *Concept clarification*: "Explain memory alignment in the context of this struct."
- *Alternative approaches*: "What are three different ways to implement this sorting algorithm?"
- *Code explanation*: "Walk through how this parser handles nested expressions."
- *Challenge generation*: "What edge cases should I test in my implementation?"

#### AI Usage Guidelines for Students
1. *Always run the code* after making AI-suggested changes
2. *Ask for explanations*, not just solutions
3. *Compare multiple AI responses* to develop critical thinking
4. *Challenge AI suggestions* with your own reasoning
5. *Document your AI interactions* as part of your learning process

#### Sample Effective Prompts
- "What might cause the segmentation fault in this memory allocator when freeing blocks?"
- "Compare the time and space complexity of my solution versus a dynamic programming approach."
- "Explain three potential solutions to this race condition and their trade-offs."
- "What design patterns might apply to restructure this code for better testability?"

### Instructor Responsibilities

#### Pre-Class Preparation
- Create or select appropriate starter code
- Test the code to ensure it works but has clear improvement opportunities
- Identify likely misconceptions and prepare guiding questions
- Develop a "theory capsule" related to the challenge
- Prepare examples of effective AI prompts for the specific task

#### During Class Facilitation
- Model problem-solving processes, including productive use of AI
- Ask Socratic questions rather than providing direct solutions
- Monitor AI usage, redirecting if students are over-reliant
- Facilitate peer learning through strategic pairing and sharing
- Provide targeted mini-lectures when common roadblocks emerge

#### Post-Class Follow-up
- Provide individual or group feedback focused on process, not just outcomes
- Share exemplary approaches (with permission) to build collective knowledge
- Connect classroom experiences to formal CS theory through readings or videos
- Reflect on lesson effectiveness and iterate on teaching approach

## 4. Creating Effective Learning Materials

### Designing Starter Code

#### Characteristics of Good Starter Code
- *Functional*: Actually runs and demonstrates core concepts
- *Accessible*: Commented appropriately for student level
- *Flawed*: Contains deliberate limitations or inefficiencies
- *Extendable*: Structured to allow meaningful modifications
- *Authentic*: Resembles real-world code (preferably beyond simple textbook examples)

#### Types of Intentional Limitations
1. *Performance issues*: Inefficient algorithms or data structures
2. *Scalability problems*: Works for small inputs but fails for larger ones
3. *Feature gaps*: Missing functionality that would make it more useful
4. *Poor design*: Working but poorly structured code that needs refactoring
5. *Edge case handling*: Fails under specific circumstances

#### Example: A Good Memory Allocator Starter Project
```c
/*
 * Simple fixed-size block allocator
 * Limitations:
 * - Only handles 32-byte blocks
 * - No coalescing of free blocks
 * - Linear search for free blocks
 */

#define MEMORY_SIZE 1024
#define BLOCK_SIZE 32

char memory[MEMORY_SIZE];
char block_used[MEMORY_SIZE / BLOCK_SIZE] = {0};

void* my_malloc(size_t size) {
    // Only handles fixed size
    if (size > BLOCK_SIZE) return NULL;
    
    // Linear search for free block
    for (int i = 0; i < MEMORY_SIZE / BLOCK_SIZE; i++) {
        if (!block_used[i]) {
            block_used[i] = 1;
            return &memory[i * BLOCK_SIZE];
        }
    }
    return NULL;  // Out of memory
}

void my_free(void* ptr) {
    // Calculate block index
    int index = ((char*)ptr - memory) / BLOCK_SIZE;
    if (index >= 0 && index < MEMORY_SIZE / BLOCK_SIZE) {
        block_used[index] = 0;
    }
}
```

### Crafting Meaningful Challenges

#### Challenge Types
1. *Extension*: Add new functionality to existing system
   - *Example*: "Add variable-sized block allocation to the memory manager"

2. *Optimisation*: Improve performance or resource usage
   - *Example*: "Reduce the time complexity of the free block search from O(n) to O(log n)"

3. *Refactoring*: Improve code structure without changing behaviour
   - *Example*: "Refactor the allocator to use a more modular design with separate data structure for tracking"

4. *Debugging*: Find and fix issues in working but flawed code
   - *Example*: "The allocator leaks memory under certain conditions - find and fix the issue"

5. *Cross-language porting*: Implement the same functionality in another language
   - *Example*: "Port the C memory allocator to a JavaScript equivalent using ArrayBuffer"

#### Challenge Progression
Structure challenges to build on each other throughout a unit:
1. *Basic modifications*: Small, well-defined changes (1-2 lines of code)
2. *Feature extensions*: Adding new capabilities (10-20 lines)
3. *Structural changes*: Redesigning components (refactoring existing code)
4. *Integration challenges*: Connecting with other systems or libraries
5. *Open-ended problems*: Multiple viable solutions requiring design decisions

### Connecting to Theory

#### Theory Integration Techniques

1. *Just-in-time mini-lectures* (5-10 minutes)
   - Triggered by common roadblocks during exploration
   - Focused specifically on concepts needed for current challenge
   - Immediately applicable to the task at hand

2. *Reflection-driven theory*
   - After students have attempted solutions, introduce formal concepts that explain observed behaviours
   - Compare student-developed approaches to canonical algorithms or patterns
   - Make explicit connections between practical experience and textbook knowledge

3. *Theory capsules*
   - Short (1-2 page) readings that formalise concepts encountered in practice
   - Assigned after hands-on experience but before refinement
   - Include comprehension questions connecting theory to project work

#### Example Theory Connection Sequence
1. Students struggle with frequent collisions in a hash table implementation
2. Instructor facilitates discussion of observed patterns
3. Mini-lecture introduces load factor and collision resolution strategies
4. Students apply theoretical knowledge to improve their implementation
5. Follow-up reading formalises concepts of hash functions and complexity analysis

## 5. Assessment & Feedback

### Process-Oriented Rubrics

A process-oriented rubric is a rubric that focuses not just on the final product (e.g. a completed program or essay), but on the quality of the process a student follows while working--things like:
- How they analyse the problem
- How they design a solution
- How they iterate and improve their work
- How they debug or reflect
- How they engage with tools (like AI) or theory

#### Comprehensive Assessment Rubric

| Criteria | Exemplary (5) | Proficient (4) | Developing (3) | Beginning (2) | Needs Work (1) |
|----------|---------------|----------------|----------------|---------------|----------------|
| Problem Analysis | Thoroughly analyses the problem, identifies key constraints and requirements, explores multiple approaches before implementation | Analyses the problem well, identifies most constraints, considers alternative approaches | Basic analysis of problem requirements, some consideration of alternatives | Limited problem analysis, jumps quickly to implementation | No evident problem analysis, trial-and-error approach |
| Solution Design | Clear architecture with appropriate abstractions, excellent modularity, anticipates future extensions | Good structure with reasonable abstractions, modular design | Basic structure with some modularity, meets immediate requirements | Poor structure with limited modularity, tightly coupled | No evident design, chaotic organisation |
| Implementation Quality | Elegant, efficient code with excellent use of language features, robust error handling | Clean, readable code with good use of language features, handles most errors | Functional code with basic use of language features, some error handling | Working but difficult to read code, minimal error handling | Incomplete or non-functioning code |
| Debugging Process | Systematic hypothesis testing, effective use of tools, clear documentation of process | Good debugging approach, uses appropriate tools, some process documentation | Basic debugging techniques, some tool usage, minimal documentation | Ad-hoc debugging, limited tool use, no documentation | No systematic debugging approach |
| AI Collaboration | Strategic AI use to explore alternatives and deepen understanding, critically evaluates suggestions | Effective AI use for specific problems, generally evaluates suggestions | Basic AI use mostly for troubleshooting, accepts most suggestions | Over-reliant on AI without understanding, accepts solutions blindly | Either doesn’t use AI or uses it to generate complete solutions |
| Theoretical Connection | Explicit connection between implementation and CS theory, can explain theoretical implications of code choices | Good connection to theory, explains most theoretical aspects | Some connection to theory, basic theoretical understanding | Limited theoretical awareness, focus only on "what works" | No connection to underlying theory |
| Iteration & Improvement | Multiple meaningful iterations with clear progression, thoughtful incorporation of feedback | Several iterations showing improvement, incorporates feedback | Some iteration, basic improvements over time | Minimal changes between versions, resistant to feedback | No iteration, single version only |
| Documentation & Communication | Exceptional documentation, clear explanations of design decisions and trade-offs | Good documentation, explains major design decisions | Basic documentation, some explanation of approach | Minimal documentation, limited explanation | No meaningful documentation |

### Portfolio Assessment

Instead of relying solely on individual assignments, you might consider a portfolio approach:

1. *Project evolution documentation*
   - Students maintain versions showing progressive improvement
   - Include reflections on key decision points and lessons learned
   - Document AI interactions and how they influenced development

2. *Process artifacts*
   - Debug logs with annotations
   - Design sketches and planning documents
   - AI prompt history with critical evaluation of responses

3. *Peer review documentation*
   - Feedback provided to other students
   - Responses to received feedback
   - Evidence of collaboration and knowledge sharing

### Reflection Prompts

Integrate these prompts into assignment submissions to encourage metacognition:

1. *Design Reflections*
   - "What alternative approaches did you consider before settling on this implementation?"
   - "How would your solution change if the input size were 100x larger?"
   - "What trade-offs did you make in your implementation and why?"

2. *Process Reflections*
   - "What was the most challenging aspect of this project and how did you overcome it?"
   - "How did your approach change from initial plan to final implementation?"
   - "If you had an additional day to work on this, what would you improve?"

3. *AI Collaboration Reflections*
   - "What questions did you ask the AI, and how did you verify its responses?"
   - "In what ways did AI help or hinder your understanding of the core concepts?"
   - "Show an example where you disagreed with or modified an AI suggestion and explain why."

4. *Theory Connections*
   - "How does your implementation relate to the concept of [relevant theory]?"
   - "What theoretical concepts became clearer through working on this project?"
   - "How would you explain the time/space complexity of your solution?"

## 6. Example Modules

### Module 1: Algorithmic Thinking

#### Week 1-2: Recursive Problem Solving

| Component | Details |
|-----------|---------|
| *Starter Code* | Naive recursive implementations of Fibonacci and factorial |
| *Challenges* | 1. Identify and fix stack overflow for large inputs<br />2. Implement memoization to improve performance<br />3. Convert to iterative implementation<br />4. Compare performance across implementations |
| *Theory Hooks* | - Recursion vs iteration<br />- Time/space complexity analysis<br />- Memoization and dynamic programming<br />- Call stack mechanics |
| *AI Prompts* | - "Why does this recursive function crash for large inputs?"<br />- "Compare the space complexity of recursive vs. iterative approaches"<br />- "How would you visualize the call stack for this function?" |
| *Assessment Focus* | - Debugging techniques<br />- Performance analysis<br />- Understanding of recursion fundamentals |

#### Week 3-4: Sorting and Searching

| Component | Details |
|-----------|---------|
| *Starter Code* | Basic implementation of quicksort with first element as pivot |
| *Challenges* | 1. Analyze and improve worst-case performance with better pivot selection<br />2. Implement hybrid sorting approach that switches to insertion sort for small partitions<br />3. Add instrumentation to count comparisons and swaps<br />4. Compare against library sort implementations |
| *Theory Hooks* | - Divide and conquer paradigm<br />- Worst/average/best case analysis<br />- Algorithm stability<br />- In-place vs. auxiliary space algorithms |
| *AI Prompts* | - "What's the impact of different pivot selection strategies?"<br />- "Why might insertion sort be faster for small arrays?"<br />- "How would you visualize the quicksort partitioning process?" |
| *Assessment Focus* | - Algorithm analysis<br />- Performance optimization<br />- Instrumentation techniques |

### Module 2: Data Structures

#### Week 5-6: Hash Tables and Collision Resolution

| Component | Details |
|-----------|---------|
| *Starter Code* | Simple hash table with linear probing and limited functionality |
| *Challenges* | 1. Implement chaining as alternative collision strategy<br />2. Add dynamic resizing when load factor exceeds threshold<br />3. Improve hash function to reduce collisions<br />4. Add deletion support with tombstone marking |
| *Theory Hooks* | - Hash function properties<br />- Load factor analysis<br />- Amortized complexity<br />- Open vs. closed addressing |
| *AI Prompts* | - "Compare advantages of chaining vs. linear probing"<br />- "What makes a good hash function for string keys?"<br />- "How would you implement a thread-safe hash table?" |
| *Assessment Focus* | - Data structure design<br />- Performance under different usage patterns<br />- Implementation trade-offs |

#### Week 7-8: Graph Representations and Traversals

| Component | Details |
|-----------|---------|
| *Starter Code* | Graph implemented as adjacency matrix with basic BFS traversal |
| *Challenges* | 1. Add DFS traversal and cycle detection<br />2. Convert to adjacency list representation<br />3. Implement Dijkstra's algorithm for shortest paths<br />4. Add support for weighted edges and directed graphs |
| *Theory Hooks* | - Graph traversal properties<br />- Space complexity of different representations<br />- Path finding algorithms<br />- Applications of graph theory |
| *AI Prompts* | - "When would you choose adjacency list over matrix?"<br />- "How would you modify BFS to find shortest path?"<br />- "What's the difference between Dijkstra's and A* algorithms?" |
| *Assessment Focus* | - Algorithm implementation<br />- Data structure selection<br />- Problem modeling using graphs |

### Module 3: Systems Programming

#### Week 9-10: Memory Management

| Component | Details |
|-----------|---------|
| *Starter Code* | Basic memory allocator with fixed-size blocks |
| *Challenges* | 1. Implement variable-sized allocation<br />2. Add block splitting and coalescing<br />3. Implement different fit strategies (first-fit, best-fit)<br />4. Add debugging features like memory usage statistics |
| *Theory Hooks* | - Memory layout and alignment<br />- Fragmentation (internal vs. external)<br />- Allocation algorithms<br />- Garbage collection concepts |
| *AI Prompts* | - "What causes fragmentation in this allocator?"<br />- "How would you implement boundary tags for coalescing?"<br />- "Compare the trade-offs between different fit strategies" |
| *Assessment Focus* | - Low-level programming<br />- Memory management concepts<br />- Debugging and monitoring |

#### Week 11-12: Concurrency and Synchronization

| Component | Details |
|-----------|---------|
| *Starter Code* | Single-threaded producer-consumer with shared buffer |
| *Challenges* | 1. Add multi-threading with locks<br />2. Identify and fix race conditions<br />3. Implement condition variables for efficiency<br />4. Add deadlock detection/prevention |
| *Theory Hooks* | - Thread safety concepts<br />- Mutex vs. semaphore<br />- Deadlock conditions<br />- Concurrent data structures |
| *AI Prompts* | - "Where are the potential race conditions in this code?"<br />- "How would you modify this to prevent deadlock?"<br />- "What's the difference between busy waiting and condition variables?" |
| *Assessment Focus* | - Concurrency understanding<br />- Synchronization mechanisms<br />- Race condition identification |

### Module 4: Software Engineering

#### Week 13-14: Testing and Debugging

| Component | Details |
|-----------|---------|
| *Starter Code* | Buggy text parser with minimal test coverage |
| *Challenges* | 1. Write comprehensive test suite including edge cases<br />2. Set up CI pipeline with automated testing<br />3. Use debugging tools to locate and fix bugs<br />4. Implement error handling and recovery |
| *Theory Hooks* | - Test-driven development<br />- Coverage metrics<br />- Debugging strategies<br />- Error handling patterns |
| *AI Prompts* | - "What edge cases should I test for this parser?"<br />- "How would you debug this segmentation fault?"<br />- "What's the difference between unit and integration tests?" |
| *Assessment Focus* | - Test design<br />- Methodical debugging<br />- Software quality practices |

#### Week 15: Code Quality and Refactoring

| Component | Details |
|-----------|---------|
| *Starter Code* | Working but poorly structured text processing application |
| *Challenges* | 1. Identify code smells and refactoring opportunities<br />2. Apply appropriate design patterns<br />3. Improve API design and documentation<br />4. Enhance maintainability without changing functionality |
| *Theory Hooks* | - SOLID principles<br />- Common design patterns<br />- Technical debt<br />- Code metrics |
| *AI Prompts* | - "What design patterns would improve this code structure?"<br />- "How would you refactor this function to improve testability?"<br />- "What metrics would you use to evaluate code quality?" |
| *Assessment Focus* | - Code organization<br />- Design pattern application<br />- Documentation quality |

## 7. Facilitating Collaborative Learning

### Pair Programming Strategies

#### Structured Pairing Approaches
1. *Driver/Navigator Rotation*
   - One student codes (driver), one directs (navigator)
   - Swap roles every 10-15 minutes
   - Navigator responsible for strategic thinking and spotting errors

2. *Ping-Pong Pairing*
   - First student writes a test
   - Second student implements code to pass the test
   - Repeat with roles reversed

3. *Strong-Style Pairing*
   - "For an idea to go from your head to the computer, it must go through someone else's hands"
   - Forces verbalization of thoughts and intentions

#### Effective Pairing Guidelines
- *Start with check-in*: Brief discussion of goals and prior knowledge
- *Set expectations*: Define roles and rotation schedule
- *Time management*: Use timers for role swaps
- *Regular retrospectives*: Brief reflections on what's working/not working
- *Balanced contribution*: Strategies for addressing skill disparities

### Group Reflection Techniques

#### Structured Sharing Formats
1. *Gallery Walk*
   - Solutions/approaches posted around room
   - Students circulate, leaving comments/questions
   - Original developers then respond to feedback

2. *Solution Auction*
   - Teams present brief pitches for their approaches
   - Class votes on most elegant, efficient, or creative solutions
   - Winners explain their thinking in detail

3. *Bug Hunt*
   - Students review other teams' code
   - Identify potential issues or edge cases
   - Original team responds to concerns

#### Reflection Facilitation Questions
- "What surprised you about your approach compared to others?"
- "Which solution best handles [specific edge case] and why?"
- "What would you do differently if you started over?"
- "How does this connect to [theoretical concept] we've discussed?"


### Building a Learning Community

#### Community-Building Practices
1. *Code Review Culture*
   - Establish constructive feedback norms
   - Focus on learning, not evaluation
   - Use "I like/I wish/What if" format

2. *Knowledge Sharing Systems*
   - Maintain class wiki of discovered techniques
   - Student-led mini-teaching sessions
   - "Expert of the week" rotating responsibility

3. *Collaborative Resources*
   - Shared prompt library for effective AI interaction
   - Error/solution database built throughout course
   - Collective debugging strategies documentation

#### Inclusive Practices
- *Multiple modes of participation*: Mix of verbal, written, and collaborative activities
- *Recognition of diverse approaches*: Highlight different valid solutions
- *Scaffolded contribution*: Clear entry points for various skill levels
- *Accessibility considerations*: Provide alternative ways to engage with materials

## 8. Troubleshooting & FAQs

### Common Challenges and Solutions

#### Student AI Over-reliance
- *Signs*: Pasting full AI outputs without understanding, unable to explain code
- *Solutions*:
  - Require written explanations of AI-suggested code
  - Ask students to modify AI solutions to meet additional requirements
  - Grade on process documentation, not just final code
  - Have students compare multiple AI suggestions and justify choices

#### Wide Skill Disparities
- *Signs*: Some students finishing quickly while others struggle to start
- *Solutions*:
  - Provide tiered challenges with common starting point
  - Create "expert consultant" roles for advanced students
  - Use pair programming with strategic pairing
  - Offer optional preparation materials before class

#### Difficulty Connecting Practice to Theory
- *Signs*: Students can implement but struggle to explain theoretical relevance
- *Solutions*:
  - Explicit bridging activities (e.g., "Map your algorithm to the theoretical model")
  - Visual aids connecting code to concepts
  - Require theoretical justification in documentation
  - Comparative analysis between implementations and textbook algorithms

#### Technical Environment Issues
- *Signs*: Significant time lost to setup and configuration
- *Solutions*:
  - Provide pre-configured environments (containers, VMs, cloud IDEs)
  - Create detailed environment setup guides
  - Dedicate first session to environment configuration
  - Have backup exercises that work with minimal setup


### Frequently Asked Questions

#### Implementation Questions
- *Q: How large should starter code projects be?*
  - A: Start small (100-300 lines) and gradually increase. Focus on conceptual complexity rather than code volume.

- *Q: How much time should I allocate for exploration vs. reflection?*
  - A: Typically 2:1 ratio (e.g., 40 min exploration, 20 min reflection), but adjust based on challenge complexity.

- *Q: What if students don't find the intended issues in the starter code?*
  - A: Prepare guiding questions to direct attention without explicitly pointing out issues. Use the reflection phase to ensure key learning happens regardless.

#### Assessment Questions
- *Q: How do I evaluate individual contribution in pair/group work?*
  - A: Combine group deliverables with individual reflections. Use peer assessments and process documentation to gauge individual contributions.

- *Q: How can I assess AI usage effectively?*
  - A: Require documentation of AI prompts and responses. Focus evaluation on how students validate, question, and modify AI suggestions.

- *Q: What about students who prefer traditional exams?*
  - A: Consider hybrid assessment with some project components and some individual theory assessments. Design "practical exams" where students modify code under time constraints.

#### AI Integration Questions
- *Q: Which AI tools are most appropriate for this teaching method?*
  - A: LLMs with code capabilities (e.g., Claude, GPT-4, GitHub Copilot). Ensure all students have equal access to chosen tools.

- *Q: How do I prevent AI from solving the entire challenge?*
  - A: Design multi-stage challenges where later requirements aren't obvious from the start. Focus on integration, optimization, and understanding rather than implementation from scratch.

- *Q: What if AI gives incorrect solutions?*
  - A: These are valuable teaching moments! Have students critically evaluate AI outputs and document where they found errors.


## 9. Resources and Tools


### Technical Resources

#### Development Environments
- *Web-based IDEs*
  - Replit (teams.replit.com) - Collaborative coding with multiplayer support
  - GitHub Codespaces - Development environments within GitHub repositories
  - CodeSandbox - Browser-based development with instant sharing

- *Local Environment Managers*
  - Docker containers with pre-configured development environments
  - VS Code with Live Share for collaborative development
  - JupyterHub for Python-focused courses

#### Starter Code Repositories
- GitHub Education organization structure
  - Template repositories for each module
  - Automated tests to verify student modifications
  - Branches representing different stages of development

#### Visualization Tools
- Algorithm visualization libraries
  - Data structure state visualization
  - Call stack tracers
  - Memory usage analyzers
  - Performance profilers


### Pedagogical Resources

#### Assessment Templates
- Process-oriented rubrics (editable versions)
- Portfolio assessment guidelines
- Peer review forms
- Reflection prompt collections

#### Classroom Management
- Pair programming rotation trackers
- Progress visualization boards
- Digital kanban for project status
- Feedback collection systems

#### Student Resources
- Debugging checklists
- Effective AI prompt templates
- Self-assessment guides
- Peer teaching guides


### AI Tools and Guidelines

#### Recommended AI Tools
- *Code-capable LLMs*
  - Accessible via web interfaces or APIs
  - Support for multiple programming languages
  - Context windows sufficient for code analysis

- *AI-augmented IDEs*
  - Code completion and suggestion features
  - Integrated explanation capabilities
  - Customizable suggestion sensitivity

#### AI Prompt Libraries
- Debugging prompt templates
- Code explanation prompts
- Alternative generation prompts
- Concept clarification prompts

#### AI Usage Guides
- Student guide to effective AI collaboration
- AI verification best practices
- Documentation templates for AI interactions
- Ethical AI usage guidelines


## 10. Further Reading

### Pedagogical Foundations
- Papert, S. (1980). *Mindstorms: Children, Computers, and Powerful Ideas*. Basic Books.
- Brown, P.C., Roediger, H.L., & McDaniel, M.A. (2014). *Make It Stick: The Science of Successful Learning*. Harvard University Press.
- Dewey, J. (1938). *Experience and education*. Macmillan.
- Kolb, D.A. (2014). *Experiential Learning: Experience as the Source of Learning and Development*. Pearson FT Press.
- Vygotsky, L.S. (1978). *Mind in Society: Development of Higher Psychological Processes*. Harvard University Press.

### Computer Science Education
- Guzdial, M. (2015). *Learner-Centered Design of Computing Education*. Morgan & Claypool.
- Nisan, N., & Schocken, S. (2005). *The Elements of Computing Systems: Building a Modern Computer from First Principles*. MIT Press.
- Hazzan, O., Lapidot, T., & Ragonis, N. (2014). *Guide to Teaching Computer Science: An Activity-Based Approach*. Springer.
- Margulieux, L., Dorn, B., & Searle, K. (2019). *Learning Sciences for Computing Education*. Cambridge University Press.
- Porter, L., & Simon, B. (2013). *Retaining Nearly One-Third More Majors with a Trio of Instructional Best Practices in CS1*. ACM SIGCSE Technical Symposium.

### AI in Education
- Roll, I., & Wylie, R. (2016). *Evolution and Revolution in Artificial Intelligence in Education*. International Journal of Artificial Intelligence in Education.
- Holstein, K., McLaren, B.M., & Aleven, V. (2019). *Co-Designing a Real-Time Classroom Orchestration Tool to Support Teacher-AI Complementarity*. Journal of Learning Analytics.
- Chen, L., Chen, P., & Lin, Z. (2020). *Artificial Intelligence in Education: A Review*. IEEE Access.

### Software Engineering Practice
- Martin, R.C. (2019). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall.
- Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code*. Addison-Wesley.
- Hunt, A., & Thomas, D. (2019). *The Pragmatic Programmer: Your Journey to Mastery*. Addison-Wesley.
- Brooks, F.P. (1995). *The Mythical Man-Month: Essays on Software Engineering*. Addison-Wesley.

(Also compare Chapter 6 on *Philosophy and Methodology*.)


## Appendix: Implementation Checklists

### Course Setup Checklist

#### Before the Semester
- [ ] Select or develop starter code repositories for each module
- [ ] Test all starter code across target environments
- [ ] Prepare environment setup instructions for students
- [ ] Design first 3-4 weeks of challenges in detail
- [ ] Create assessment rubrics and portfolio templates
- [ ] Configure AI tools and prepare usage guidelines
- [ ] Set up collaborative platforms (version control, discussion forums)

#### First Week
- [ ] Environment setup session
- [ ] AI tool introduction and practice
- [ ] Establish collaboration norms and expectations
- [ ] Simple modification challenge to build confidence
- [ ] Initial reflection on process

#### Ongoing Maintenance
- [ ] Weekly review of progress and pacing
- [ ] Regular collection of student feedback
- [ ] Adjustment of challenge difficulty based on observations
- [ ] Documentation of successful/unsuccessful activities
- [ ] Regular updates to FAQ and troubleshooting guides

### Lesson Planning Checklist

#### Preparation Phase
- [ ] Identify core concept(s) to address
- [ ] Select or create appropriate starter code
- [ ] Test code with intended modifications
- [ ] Prepare guiding questions for exploration
- [ ] Create theory connection materials
- [ ] Develop reflection prompts
- [ ] Plan for common misconceptions/roadblocks

#### Delivery Phase
- [ ] Clear introduction of challenge and constraints
- [ ] Demonstration of starter code functionality
- [ ] Guided initial exploration strategies
- [ ] Strategic circulation during work time
- [ ] Timely interventions for common issues
- [ ] Facilitation of meaningful reflection
- [ ] Explicit connections to theoretical concepts

#### Follow-up Phase
- [ ] Provide individual/team feedback
- [ ] Share exemplary approaches
- [ ] Connect to upcoming challenges
- [ ] Update documentation based on classroom experiences
- [ ] Reflect on lesson effectiveness

## Conclusion

This project-first, AI-supported approach represents a fundamental shift in computer science education—moving from abstract theory to contextualized learning through authentic tasks. By embracing the realities of modern software development, including the role of AI as a thinking partner, we prepare students not just for academic success but for the actual practice of computer science in industry and research.

The approach adapts as technology evolves, with AI tools becoming increasingly sophisticated partners in the learning process. However, the core principles remain constant: learning through modification of existing systems, embracing productive struggle, connecting practice to theory, and fostering a collaborative learning community.

As you implement this approach, remember that the goal is not perfect projects but perfect learning—students who develop the confidence, skills, and understanding to tackle complex computing challenges with creativity and rigor. The true measure of success is not what your students can build by the end of the course, but what they can learn to build in the years that follow.

