
## Crafting vs. TDD: Code as Exploration vs. Specification

*Ok, so I have some issues with TDD .. How do I resolve this?*


### Two Faces of Code  

Code serves dual purposes:  
- *Code as Thought*: A medium for exploration, experimentation, and understanding (e.g., prototyping
  an algorithm to test feasibility).  
- *Code as Product*: A polished artefact optimised for correctness, maintainability, and scalability.  

Argument: *TDD conflates these purposes* by requiring tests upfront, which assumes the problem is
already well-understood. This risks locking in assumptions prematurely, stifling innovation in
ambiguous or novel domains.


### The Innovation Paradox in TDD  

*Why TDD can hinder exploration*:  
- *Premature Lock-In*: Tests encode today's understanding, creating inertia if (future) requirements shift.  
- *Architectural Blindness*: Focus on unit tests obscures systemic properties (e.g., scalability, data flow).  
- *Cognitive Overhead*: Writing tests for poorly understood domains (e.g., AI) feels like "describing a
  color you've never seen."  

*Where TDD shines*:  
- Stable contexts (e.g., CRUD apps).  
- Collaborative environments needing shared specifications.  
- Refactoring with confidence.  


### Crafting as a Counterpoint  

A *crafting approach* prioritises code as a tool for thinking, enabled by LLMs:  
1. *Sketch*: Write raw code to explore ideas (e.g., "Can LLMs generate API specs?").  
2. *Expand*: Refactor with LLMs into modular components.  
3. *Critique*: Ask LLMs, *"What scalability risks does this ignore?"*  
4. *Harden*: Add tests *after* patterns emerge.  

*Why this fosters innovation*:  
- *Late Decision Binding*: Architectural commitments delay until patterns crystallise.  
- *Fluid Feedback*: LLMs propose alternatives (e.g., *"Would serverless simplify this?"*).  
- *Serendipity*: Accidental discoveries are nurtured (e.g., a helper function becoming a core service).  


### Where Crafting Risks Failure  

*Trade-offs*:  
- *Chaos at Scale*: Unstructured exploration risks incoherent systems.  
- *Documentation Debt*: Fluid designs lack decision trails (mitigate with LLM-generated ADRs).  
- *Client Anxiety*: Stakeholders may fear "endless tinkering" (solve with frequent demos).  

*Critique of the Crafting View*:  
- *Romanticising Ambiguity*: Not all problems need exploration (e.g., dentist appointment apps).  
- *Underestimating Tests*: Even prototypes need sanity checks (e.g., validating LLM output).  


### Synthesis: When to Craft, When to Specify  

| *Context*              | *Crafting + LLMs*                          | **TDD/Architecture-First**            |  
|------------------------|--------------------------------------------|---------------------------------------|  
| *Novel Domains*        | Essential (e.g., AI, blockchain).          | Risky (requires clairvoyance).        |  
| *Legacy Integration*   | Use LLMs to reverse-engineer constraints.  | Necessary for safety (e.g., banking). |  
| *High-Stakes Systems*  | Prototype only; harden with TDD.           | Mandatory (avoids liability).         |  
| *Startup MVPs*         | Ideal (fast pivots).                       | Overkill (unless regulated).          |  



### A Hybrid Future  

*Workflow*:  
1. *Craft*: Brainstorm with LLMs (no tests, just code sketches).  
2. *Correlate*: LLMs extract patterns and propose architecture.  
3. *Commit*: Test-drive the stable core, leave room for experimentation.  

*LLMs as Mediators*:  
- Translate between mindsets (e.g., *"Your code implies microservices--here's how to test-drive the first service"*).  
- Auto-generate tests for critical paths.  


### Conclusion  

TDD prioritises certainty over curiosity, which stifles innovation in ambiguous domains. The solution is to *stage rigour*:  
1. Use crafting and LLMs to navigate uncertainty.
2. Apply TDD and architectural principles to establish stable paths.
- Use tests to strengthen the code, not to rigidly define the architecture.
- Apply testing as early as possible; don’t wait until the code is fully hardened.
3. Let LLMs bridge the gap between exploration and discipline.

The future lies in tools that embrace both--code as a dialogue between the unknown and the engineered.

