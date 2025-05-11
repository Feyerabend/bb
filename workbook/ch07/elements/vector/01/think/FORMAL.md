
## IDEAS: Intelligent Development with Enhanced Assistance and Support

*Version 0.1: Draft Model.*


#### Phase 1: Communicate: Understand the Problem

* *Goal*: Establish a shared understanding of the problem space and client goals.
* *Inputs*: Conversations, existing workflows, business needs.
* *Outputs*: Domain vocabulary, core user stories, initial usage scenarios.

Activities:
- Conduct free-form discussions (LLM assists in summarising and reframing).
- Elicit goals, pain points, success criteria.
- Use LLM to generate example use cases, mock dialogs, process maps.


#### Phase 2: Familiar Prototype: Ground in the Known

* *Goal*: Quickly build a tangible prototype of features the client already understands.
* *Inputs*: User stories, existing workflows, legacy systems.
* *Outputs*: Clickable mockups, data views, simple workflows.

Activities:
- Use LLM to scaffold UI sketches, database mocks, example outputs.
- Implement trivial workflows first (no new technical risk).
- Demo and validate continuously with client.


#### Phase 3: Data Landscape: Map and Explore the Data

* *Goal*: Inventory, understand, and evaluate the available data.
* *Inputs*: Databases, APIs, files, user-generated content.
* *Outputs*: Data catalog, schemas, data quality profiles.

Activities:
- Use LLM to extract schemas, profile datasets, generate sample data.
- Document data ownership, access rights, privacy concerns.
- Prioritise interesting or valuable data (not necessarily what's easiest).


#### Phase 4: Incremental Build: Layer New Functionality

* *Goal*: Gradually add more complex or novel features atop familiar foundations.
* *Inputs*: Validated prototypes, data profiles, client feedback.
* *Outputs*: Working system with growing feature set.

Activities:
- Use LLM to generate boilerplate code, integrations, and tests.
- Implement one novel feature at a time, always demoing after each step.
- Simulate or stub complex components with LLM-generated mocks if needed.


#### Phase 5: Validate: Close the Feedback Loop

* *Goal*: Continuously ensure the solution matches evolving client understanding.
* *Inputs*: System demos, user feedback, test cases.
* *Outputs*: Adjusted requirements, bug reports, enhancement requests.

Activities:
- Use LLM to summarise sprint progress, auto-generate release notes, visualise workflows.
- Conduct lightweight user testing or data validation sessions.
- Rapidly iterate based on new insights.


#### Phase 6: Harden: Prepare for Real-World Use

* *Goal*: Optimise, secure, and finalise the product for production.
* *Inputs*: Fully functional system, validated features.
* *Outputs*: Production-grade software, documentation, deployment pipelines.

Activities:
- Use LLM to review code for security, generate docs, write deployment scripts.
- Replace mocks/stubs with real integrations.
- Optimise performance and scalability.


### Summary

|Phase	|Main Goal	|LLM Role|
|--|--|--|
|Communicate	|Understand problem & goals	|Summarise, generate scenarios|
|Familiar Prototype	|Build trivial, known features	|Scaffolding, mockups|
|Data Landscape	|Map available data	|Profile, summarise, simulate datasets|
|Incremental Build	|Add new features gradually	|Code generation, test generation|
|Validate	|Align with evolving understanding	|Summarise progress, auto-generate reports|
|Harden	|Optimise & deploy	|Review code, generate docs & scripts|

Process: *Communicate → Familiar Prototype → Data Landscape → Incremental Build → Validate → Harden.*


#### Key Principles
- *Clarity before Complexity*: Only build complex things when simpler ones are working and understood.
- *Data before Logic*: Understand data deeply before writing heavy logic.
- *Continuous Client Contact*: Small, frequent demos beat big-bang deliveries.
- *LLM as Augmented Colleague*: Use it constantly, but always validate output critically.
