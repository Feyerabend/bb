
## Data in a Farmacy

A dialog between Jamie (the programmer) and Morgan (an administrator in the healthcare system)
to tackle a problem involving handling medical receipts, patients, doctors, and pharmacies.
The focus will again be on reasoning about the problem and designing a language to express solutions.

__Scene__: *A conference room with a large table covered in printed receipts, reports, and some laptops.*

__Morgan__: Jamie, our healthcare data is a mess. We've got medical receipts from patients, prescriptions
from doctors, and billing records from pharmacies, all in different formats. Every time we try to compile
reports--say, which doctor prescribed the most or how much a patient's treatment cost--it's a nightmare.

__Jamie__: Sounds frustrating. It also sounds like a perfect case for creating a consistent way to describe
this data. Have you thought about approaching this as a language problem?

__Morgan__: A language? No, we just want a system that can handle all the data and generate reports.

__Jamie__: A system is great, but it's only as good as its design. What if we first design a language for
your domain--a structured way to describe and manipulate this data? Then, we can build the system around
that language.

__Morgan__: Alright, I'm intrigued. Where do we start?

__Jamie__: Let's start with the vocabulary. What are the main entities you deal with in your work?

__Morgan__: Patients, doctors, pharmacies, prescriptions, receipts, and payments. Those are the big ones.

__Jamie__: Good. Each of those is a key concept in our language. Now, what information do you need to
capture about each?

__Morgan__: For patients, we need their personal details--name, age, ID—and their medical history.
For doctors, it's their credentials, specialties, and prescriptions written. Pharmacies need their
location and the drugs they dispense. Receipts tie all this together: they show who received what
treatment, prescribed by whom, filled where, and how much it cost.

__Jamie__: Got it. Let's take an example and map it out. Say a patient visits a doctor, gets a
prescription, and fills it at a pharmacy. What's the smallest "story" you'd need to tell to describe
that interaction?

__Morgan__: Something like: "Patient A was prescribed Drug B by Doctor C, filled it at Pharmacy D, and paid $X."

__Jamie__: Perfect. That's our grammar—how we structure these interactions. We can represent it like this:

```json
{
  "patient": {"id": "A", "name": "John Doe"},
  "prescription": {
    "drug": {"name": "Drug B", "dose": "10mg"},
    "doctor": {"id": "C", "name": "Dr. Smith"}
  },
  "pharmacy": {"id": "D", "name": "Pharmacy D"},
  "payment": {"amount": 100.0, "currency": "USD"}
}
```

__Morgan__: That makes sense for one interaction. But we also need to analyze trends—like total spending
per patient or which drugs a doctor prescribes most often.

__Jamie__: Good point. That's where we need to add verbs—operations in the language to query and manipulate
this data. For instance:

```
"Summarize total spending for Patient A over the past year."
"Rank drugs prescribed by Doctor C by frequency."
```

These could be expressed as operations in the language:

```json
{
  "operation": "summarize",
  "target": "spending",
  "filter": {"patient_id": "A", "date_range": ["2023- 01- 01", "2023- 12- 31"]}
}
```

or

```json
{
  "operation": "rank",
  "target": "drugs",
  "filter": {"doctor_id": "C"},
  "criteria": "frequency"
}
```

__Morgan__: This is starting to feel intuitive. We're building a way to describe not just the data but
what we want to do with it.

__Jamie__: Exactly. It's all about expressiveness. Over time, we can make this language richer by adding
new concepts, like insurance claims or drug interactions. For example, we might define a new type of relationship:

```json
{
  "patient": {"id": "A"},
  "insurance": {"id": "Plan Z", "coverage": 0.8},
  "claim": {"amount_requested": 100, "amount_covered": 80}
}
```

__Morgan__: But what about flexibility? Our data is constantly evolving. For instance, a prescription
might contain multiple medications, or a pharmacy might offer delivery instead of in-store dispensing.

__Jamie__: That's a great observation. We can handle variability by building the language around extensibility.
For instance, prescriptions could be a list of drugs instead of a single one, and pharmacies could have
optional attributes like "delivery service."

```json
{
  "prescription": {
    "drugs": [
      {"name": "Drug B", "dose": "10mg"},
      {"name": "Drug C", "dose": "5mg"}
    ],
    "doctor": {"id": "C", "name": "Dr. Smith"}
  },
  "pharmacy": {
    "id": "D",
    "name": "Pharmacy D",
    "delivery": {"status": true, "date": "2023- 12- 15"}
  }
}
```

__Morgan__: I like it. We're designing a language that grows with our needs.

__Jamie__: Exactly. And once we have this language, we can build tools--a database schema, a reporting system,
or even a user interface—on top of it. The tools aren't the end goal; they're expressions of the language.

__Morgan__: So, the language becomes the foundation. It lets us describe, analyze, and evolve our processes,
all in a structured way.

__Jamie__: You've got it. It's like creating a grammar for your administrative work, where the syntax describes
your data and the operations express what you want to do with it. Over time, this will make your system more
transparent, adaptable, and aligned with how you think about your work.


## Making Programs from Data

This dialog shows how reasoning about a problem as a language design exercise can bring clarity and flexibility
to complex administrative tasks. By focusing on the vocabulary, grammar, and operations needed to describe
and manipulate data, Jamie and Morgan create a framework that can adapt as their needs evolve, much like a
natural language evolves to describe new concepts.

Expanding on the healthcare administration language example, let's explore how this approach might evolve.
We'll outline the next steps, sketch the development process, and imagine how this custom language could
solve problems and shape the final product.

#### 1. Refining the Language Design

__Next Step: Iterative Refinement__

After the initial design of the language (vocabulary, grammar, and basic operations), the next step is to
refine it by:

1. Gathering Feedback: Collaborate with stakeholders (administrators, doctors, pharmacists) to identify
   edge cases and missing concepts.

2. Defining the Syntax: Decide on a user-friendly format for writing and reading the language. For example,
   should it be JSON, YAML, or something closer to natural language?

3. Formalizing the Semantics: Define precisely how each operation (e.g. "summarise," "rank") will behave.
   This could involve designing algorithms for aggregation, filtering, and ranking.

Sketch of Progress:
- Expand the vocabulary to include entities like insurance plans, claim statuses, or drug manufacturers.
- Extend the grammar to support conditional logic (e.g. "if insurance coverage is less than 50%, flag the claim").
- Introduce reusable templates, such as a standard prescription format or a common report structure.

Example:

A template for analyzing patient spending by drug category might look like:

```json
{
  "template": "spending_analysis",
  "parameters": {
    "patient_id": "A",
    "group_by": "drug_category",
    "date_range": ["2023- 01- 01", "2023- 12- 31"]
  }
}
```

#### 2. Building Supporting Tools

__Next Step: Implementation__

With the language design solidified, the next step is to build tools that let users express and
execute tasks in the language.

Tools to Develop:
1. Interpreter/Engine: A core engine that understands the language, executes operations, and
   interfaces with the underlying data storage.
2. User Interface (UI): A front- end application where non- technical users can interact with
   the language without writing code directly. For instance, a drag-and-drop report builder that
   generates language constructs under the hood.
3. APIs: Expose the language to other systems via APIs, enabling integration with electronic
   medical records (EMRs) or pharmacy management systems.

Sketch of Progress:
- Implement a query engine that processes commands like "summarize patient spending."
- Build a visual editor where users define operations by selecting options, which are then
  translated into the language.

#### 3. Solving Problems and Evolving the System

Problem-Solving Workflow:

With the system in place, the language enables solving problems in structured and repeatable ways:
1. Describing Problems: Users express problems as queries or templates in the language. For
   instance, "Find all prescriptions from Doctor X that were not filled within 7 days."
2. Customizing Solutions: The language allows for customization. For example, pharmacies could
   define a workflow: "If a prescription is flagged as urgent, notify the pharmacist within 1 hour."
3. Automating Decisions: As the language evolves, it can automate tasks, such as generating monthly
   reports or identifying anomalies in spending patterns.

Example Problems Solved:
- Auditing Receipts:

Language Query:

```json
{
  "operation": "audit",
  "target": "receipts",
  "filter": {
    "discrepancy": true
  }
}
```

Outcome: The system identifies all receipts with discrepancies between prescribed and dispensed amounts.
- Tracking Compliance:

Language Query:

```json
{
  "operation": "compliance_check",
  "target": "pharmacies",
  "criteria": {
    "prescription_fill_rate": {"threshold": 95}
  }
}
```

Outcome: Generate a report showing pharmacies with fill rates below the compliance threshold.

#### 4. Evolving the Language

Adding New Features:

As users interact with the system, new needs will emerge, prompting the language to evolve:
1. Higher Abstractions: Add constructs for recurring tasks, like "generate monthly compliance summary."
2. Complex Workflows: Introduce conditional logic and triggers, e.g., "If a payment is overdue by 30 days, send a reminder."
3. Learning and Adaptation: Integrate machine learning to enable predictive queries, like
   "Which patients are at risk of missing their next prescription?"

Example:

Adding machine learning for fraud detection:

```json
{
  "operation": "detect_anomalies",
  "target": "receipts",
  "criteria": {"model": "fraud_detection_v1"}
}
```

#### 5. The Final Product

How It Works:
1. User Interaction: Administrators use the system through an intuitive UI or directly via the language to define queries, reports, and workflows.
2. Execution: The interpreter processes commands, retrieves and manipulates data, and delivers results in real-time.
3. Integration: APIs enable seamless integration with other systems, automating the flow of information between stakeholders.

Benefits:
- Transparency: Every operation is described in the language, creating an auditable and clear record of what's being done.
- Flexibility: The language adapts to new requirements, making it future-proof.
- Efficiency: Common tasks are automated, and complex problems are expressed succinctly.

Example in Action

Morgan logs into the system to analyze pharmacy performance for the month. Using the visual UI, they create a query to rank pharmacies by prescription fill rates. The system translates their input into the language:

```json
{
  "operation": "rank",
  "target": "pharmacies",
  "criteria": "fill_rate",
  "date_range": ["2024- 01- 01", "2024- 01- 31"]
}
```

The query runs, and the result is a ranked list of pharmacies, highlighting those that need attention. Morgan notices an outlier and digs deeper:

```json
{
  "operation": "analyze",
  "target": "pharmacy",
  "filter": {"id": "D", "date_range": ["2024- 01- 01", "2024- 01- 31"]}
}
```

The system reveals that Pharmacy D has a delayed response time for urgent prescriptions. Morgan adjusts workflows to
address the issue, directly from the interface.

This iterative approach—designing the language, building tools, solving problems, and evolving the system—creates a
dynamic, user-driven platform for tackling administrative challenges. The language grows to reflect the complexity
of the domain while remaining accessible, empowering users to think clearly and act decisively.


