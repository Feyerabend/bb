
## Project Plan: Programming Paradigms Hybrid Project

This project plan provides a structured yet flexible way to engage students with programming paradigms.
It balances philosophical exploration with practical application, making it suitable for a diverse classroom.


### Project Overview

You will create a *mini-manifesto* articulating their principles for approaching programming problems and
apply these principles by designing a *mini-methodology* (e.g., a domain-specific language or a resilience-focused
system) for a chosen problem domain. The project draws inspiration from the documents in the folders,
particularly the dialogues contrasting traditional and language-driven approaches. The goal is to encourage
critical thinking about programming paradigms while providing hands-on experience with designing and
(optionally) implementing a solution.

*Possible Target Audience*: Undergraduate or early graduate students in computer science or related fields,
with varying programming experience.

*Duration*: 4-6 weeks (adjustable based on class schedule).

*Learning Objectives*:
1. Understand and compare different programming paradigms (e.g., traditional, language-driven, resilience-focused).
2. Articulate personal principles for problem-solving in programming through a manifesto.
3. Design a methodology (e.g., a DSL or system architecture) that reflects their principles.
4. Reflect on the trade-offs and implications of different paradigms.
5. (Optional) Implement a prototype to demonstrate their methodology.



### Project Phases and Prompts

#### Phase 1: Exploration (Week 1)

*Goal*: Introduce students to programming paradigms and prepare them to articulate their own principles.

*Activities*:
- *Reading and Discussion*:
  - Assign excerpts from your documents:
    - `CONTRAST.md`: Dialogue between Jordan and Casey to contrast language-driven vs. traditional approaches.
    - `DIALOG-LIBRARY.md`: Dialogue on designing a DSL for library management.
    - `RESILIENCE.pdf`: Sections 3 (Manifesto) and 4 (Methodologies) for resilience principles.
  - Hold a class discussion or small-group activity to compare paradigms. Example questions:
    - How does Jordan's language-driven approach differ from Casey's traditional approach? What are the trade-offs?
    - Why might a library benefit from a DSL instead of a standard database system?
    - How do resilience principles like error budgeting or chaos engineering change the way we think about software?
- *Brainstorming*:
  - Students brainstorm a problem domain they're interested in (e.g., event planning, pet adoption, task scheduling, disaster response). Provide a list of example domains for inspiration:
    - Library management (books, patrons, borrowings)
    - Event ticketing (events, attendees, payments)
    - Pet adoption (pets, adopters, matches)
    - Disaster response (resources, responders, locations)
  - Prompt: "Choose a problem domain that interests you. Write a 1-paragraph description of the domain and list
    3-5 key entities or concepts (e.g., books, patrons, resources)."

*Deliverable*:
- A 1-page document with:
  - A chosen problem domain and its description.
  - A list of 3-5 key entities/concepts.
  - A short reflection (100-150 words) on how the assigned readings influenced their choice.

*Prompt*:
> In this phase, you'll explore different programming paradigms through provided readings and select a problem
  domain to focus on. Read the assigned excerpts and participate in class discussions to compare traditional,
  language-driven, and resilience-focused approaches. Then, choose a problem domain (e.g., library management,
  event ticketing) and write a 1-paragraph description of it, including 3-5 key entities or concepts. Conclude
  with a short reflection (100-150 words) on how the readings shaped your understanding of programming paradigms
  and influenced your domain choice.



#### Phase 2: Mini-Manifesto (Week 2)

*Goal*: Students articulate their personal principles for approaching programming problems.

*Activities*:
- *Lecture/Guidance*:
  - Provide a mini-lecture on manifestos, using `RESILIENCE.pdf` (Section 3) as an example. Highlight how principles like
    "embrace risk" or "automate everything" guide decision-making.
  - Discuss how your `README.md` advocates for a language-driven approach, emphasizing data and expressiveness.
  - Share a simplified manifesto template:
    - Principle 1: [Statement] (e.g., "Prioritise flexibility over premature optimisation")
    - Justification: [Why this matters, with an example]
    - Principle 2: [Statement]
    - Justification: [Why this matters, with an example]
    - etc.
- *Writing*:
  - Students write a mini-manifesto with 3-5 principles for how they approach programming. Each principle should include
    a 1-2 sentence justification and an example (e.g., from their chosen domain or class readings).
  - Students, you, are encouraged to draw inspiration from the paradigms discussed (traditional, language-driven,
    resilience-focused) but also to incorporate their own ideas!

*Deliverable*:
- A 1-2 page mini-manifesto with 3-5 principles, each with a justification and example.

*Prompt*:
> Create a mini-manifesto outlining 3-5 principles for how you approach programming problems. Each principle should be
  a clear statement (e.g., "Design for adaptability") followed by a 1-2 sentence justification explaining why it matters
  and an example (e.g., from your chosen problem domain or class readings). Draw inspiration from the paradigms we've
  discussed (traditional, language-driven, resilience-focused) but feel free to include your own ideas. Your manifesto
  should reflect your personal philosophy and guide your approach to the next phase of the project.



#### Phase 3: Mini-Methodology Design (Weeks 3-s4)

*Goal*: Students design a methodology (e.g., a DSL or resilience-focused system) for their chosen domain, reflecting
their manifesto principles.

*Activities*:
- *Lecture/Guidance*:
  - Explain the concept of a methodology, using examples from your documents:
    - DSL design in `DIALOG-LIBRARY.md` (vocabulary, grammar, operations).
    - Resilience principles in `RESILIENCE.pdf` (redundancy, fault tolerance, chaos engineering).
  - Provide a template for methodology design:
    - *Domain Description*: Brief recap of the problem domain.
    - *Vocabulary*: Key entities/concepts and their attributes (e.g., books, patrons).
    - *Grammar*: How entities relate (e.g., "Patron borrows Book").
    - *Operations*: Actions or queries (e.g., "find overdue books," "allocate resources").
    - *Manifesto Alignment*: How the methodology reflects their principles.
    - (Optional) *Resilience Features*: For advanced students, include features like fault tolerance or observability.
  - Offer examples of JSON-based DSLs (e.g., from `DIALOG-LIBRARY.md`):
    ```json
    {
      "operation": "find",
      "target": "overdue_books",
      "filter": {"patron_id": "A"}
    }
    ```
- *Design*:
  - Students design a methodology for their domain, specifying vocabulary, grammar, and operations. Beginners can use
    JSON or pseudocode; intermediate/advanced students can include resilience features or a prototype plan.
  - You are encouraged to align your methodology with your manifesto (e.g., if a principle is "prioritise expressiveness,"
    the DSL should be intuitive for domain experts).

*Deliverable*:
- A 2-3 page methodology document with:
  - Domain description (1 paragraph).
  - Vocabulary (list of entities/concepts with attributes).
  - Grammar (description or examples of relationships).
  - Operations (3-5 example commands/queries in JSON or pseudocode).
  - Manifesto alignment (1-2 paragraphs explaining how the methodology reflects their principles).
  - (Optional) Resilience features or prototype plan for advanced students.

*Prompt*:
> Design a mini-methodology for your chosen problem domain, reflecting the principles in your manifesto. Your
  methodology could be a domain-specific language (DSL) or a resilience-focused system architecture. Include:
  (1) a brief domain description,
  (2) a vocabulary of key entities/concepts with attributes,
  (3) a grammar showing how entities relate,
  (4) 3-5 operations (commands/queries in JSON or pseudocode), and
  (5) 1-2 paragraphs explaining how your methodology aligns with your manifesto. Optionally, for advanced students,
  include resilience features (e.g., fault tolerance, observability) or a plan for a prototype implementation.



#### Phase 4: (Optional) Prototype Implementation (Week 5)

*Goal*: Advanced or intermediate students implement a simple prototype of their methodology
(e.g., a DSL interpreter or a resilient system).

*Activities*:
- *Guidance*:
  - Provide starter code (see below) for a basic DSL interpreter in Python, which students can adapt for their methodology.
  - For resilience-focused systems, suggest libraries like `Flask` (Python) or `Express` (Node.js) for building a simple
    API with fault tolerance (e.g., retry logic).
  - Offer tutorials or office hours for tools like JSON parsing, basic APIs, or logging for observability.
- *Implementation*:
  - Beginners: Modify the starter code to process 1-2 commands from their DSL.
  - Intermediate: Build a full interpreter for their DSL with 3-5 operations or a simple API with basic resilience (e.g., retries).
  - Advanced: Implement a robust prototype with resilience features (e.g., circuit breakers, logging) or integrate with
    an LLM for natural language input.

*Deliverable*:
- A working prototype (code submitted via GitHub or similar) with:
  - A README explaining how to run it.
  - A demo of 1-5 operations or features.
- A 1-page report summarizing the prototype and its alignment with the manifesto.

*Prompt*:
> (Optional for intermediate/advanced students) Implement a prototype of your methodology, such as a DSL interpreter or
  a resilience-focused system. Use the provided starter code or a framework of your choice (e.g., Python, Node.js).
  Your prototype should demonstrate at least 1-5 operations or features from your methodology. Submit your code with a
  README explaining how to run it and a 1-page report summarizing the prototype and how it aligns with your manifesto
  principles. Advanced students may include resilience features (e.g., retries, logging) or integrate with an LLM
  for natural language input.



#### Phase 5: Presentation and Reflection (Week 6)

*Goal*: Students share their work, reflect on their learning, and refine their perspectives.

*Activities*:
- *Presentations*:
  - Students present their manifesto and methodology (5-7 minutes each) to the class, focusing on:
    - Key principles and why they matter.
    - How their methodology addresses the domain problem.
    - Trade-offs or lessons learned.
  - Encourage peer feedback (e.g., "What did you find innovative about this methodology?").
- *Reflection*:
  - Students write a reflective essay on how their views on programming evolved and how they
    might apply their principles in future work.

*Deliverables*:
- A 5-7 minute presentation (slides or live demo optional).
- A 1-2 page reflective essay answering:
  - How did designing a manifesto and methodology change your view of programming?
  - What challenges did you face, and how did you overcome them?
  - How might you apply your principles in a real-world project?

*Prompt*:
> Prepare a 5-7 minute presentation to share your mini-manifesto and methodology with the class.
  Highlight your key principles, explain how your methodology addresses your domain problem, and
  discuss trade-offs or lessons learned. Submit a 1-2 page reflective essay answering:
  (1) How did this project change your view of programming?
  (2) What challenges did you face, and how did you overcome them?
  (3) How might you apply your principles in a real-world project?
  Provide constructive feedback to at least two peers during presentations.



### Rubric

| *Category* | *Excellent (4)* | *Good (3)* | *Fair (2)* | *Needs Improvement (1)* |
|--------------|-------------------|--------------|--------------|--------------------------|
| *Manifesto (20%)* | 3-5 clear, insightful principles with strong justifications and relevant examples. Reflects deep engagement with paradigms. | 3-5 principles with clear justifications and examples. Shows some engagement with paradigms. | 3-5 principles, but justifications or examples are vague or incomplete. Limited engagement with paradigms. | Fewer than 3 principles, or principles lack clarity, justification, or examples. |
| *Methodology Design (30%)* | Vocabulary, grammar, and operations are well-defined, creative, and domain-specific. Strong alignment with manifesto. | Vocabulary, grammar, and operations are defined and relevant. Clear alignment with manifesto. | Vocabulary, grammar, or operations are incomplete or unclear. Weak alignment with manifesto. | Methodology is poorly defined or unrelated to domain/manifesto. |
| *Prototype (20%)* (Optional) | Prototype is functional, demonstrates 3-5 operations/features, and aligns with methodology. Includes clear README and report. | Prototype is functional, demonstrates 1-3 operations/features, and aligns with methodology. Includes basic README/report. | Prototype is partially functional or demonstrates limited features. README/report is incomplete. | Prototype is non-functional or missing key components. |
| *Presentation (15%)* | Engaging, clear presentation with insightful discussion of principles, methodology, and trade-offs. | Clear presentation covering key points. Some discussion of trade-offs. | Presentation is unclear or misses key points. Limited discussion of trade-offs. | Presentation is disorganized or incomplete. |
| *Reflection (15%)* | Thoughtful essay with deep insights on learning, challenges, and future applications. | Clear essay with some insights on learning and challenges. | Essay is vague or lacks depth in addressing learning or challenges. | Essay is incomplete or superficial. |



### Starter Code

Below is a simple Python-based DSL interpreter that you can adapt for your methodology.
It processes JSON commands for a generic library system but can be modified for other domains.
This is suitable for beginners to intermediate students.

```python
# dsl_interpreter.py
import json

# sample database (in-memory, could be replaced with a real DB)
library_db = {
    "books": [
        {"id": "B1", "title": "The Great Adventure", "author": "John Smith", "status": "available"},
        {"id": "B2", "title": "Mystery Island", "author": "Jane Doe", "status": "checked out"}
    ],
    "patrons": [
        {"id": "P1", "name": "Alice Doe", "borrowed_books": ["B2"]}
    ],
    "borrowings": [
        {"book_id": "B2", "patron_id": "P1", "date_borrowed": "2025-01-01", "due_date": "2025-01-15"}
    ]
}

def find_overdue_books(command):
    """Process a 'find' operation for overdue books."""
    current_date = command["filter"].get("current_date", "2025-01-01")
    patron_id = command["filter"].get("patron_id")
    
    overdue_books = []
    for borrowing in library_db["borrowings"]:
        if borrowing["due_date"] < current_date:
            if not patron_id or borrowing["patron_id"] == patron_id:
                book = next(b for b in library_db["books"] if b["id"] == borrowing["book_id"])
                overdue_books.append(book)
    
    return {"overdue_books": overdue_books}

def count_borrowed_books(command):
    """Process a 'count' operation for borrowed books."""
    patron_id = command["filter"].get("patron_id")
    if not patron_id:
        return {"error": "Patron ID required"}
    
    patron = next((p for p in library_db["patrons"] if p["id"] == patron_id), None)
    if not patron:
        return {"error": "Patron not found"}
    
    return {"count": len(patron["borrowed_books"])}

# dispatcher for operations
operations = {
    "find": find_overdue_books,
    "count": count_borrowed_books
}

def process_command(command_str):
    """Process a JSON command string."""
    try:
        command = json.loads(command_str)
        operation = command.get("operation")
        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}
        
        return operations[operation](command)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}

# Example
if __name__ == "__main__":

    # command: Find overdue books
    command1 = '''
    {
        "operation": "find",
        "target": "overdue_books",
        "filter": {"current_date": "2025-01-16", "patron_id": "P1"}
    }
    '''
    print(json.dumps(process_command(command1), indent=2))
    
    # command: Count borrowed books
    command2 = '''
    {
        "operation": "count",
        "target": "borrowed_books",
        "filter": {"patron_id": "P1"}
    }
    '''
    print(json.dumps(process_command(command2), indent=2))
```

*How Students Use It*:
- *Beginners*: Modify the `library_db` to match their domain (e.g., pets instead of books)
  and add one new operation (e.g., "match pet to adopter").
- *Intermediate*: Add 2-3 new operations and update the database structure to support their DSL grammar.
- *Advanced*: Integrate resilience features (e.g., retry logic for database access)
  or add a REST API to process commands via HTTP.



### Teachers: Additional Notes

- *Scaffolding for Beginners*: A simplified JSON template and a step-by-step guide for
  modifying the starter code. For example:
  ```json
  {
    "operation": "[your_operation]",
    "target": "[your_target]",
    "filter": {"[key]": "[value]"}
  }
  ```
- *Support for Advanced Students*: Suggest libraries like `requests` for API integration, 
  `structlog` for structured logging, or `tenacity` for retries. Encourage exploration of
  LLMs (e.g., via API calls to a model like Grok) for generating DSL syntax.
- *Time Management*: If 6 weeks is too long, compress Phases 3-4 into 2 weeks by focusing
  on design for beginners and limiting prototype scope for advanced students.
- *Assessment*: Use the rubric to provide clear expectations. Offer formative feedback
  after Phase 2 (Manifesto) to help students refine their methodology.
