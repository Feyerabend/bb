
## Language About Data: Shaping the Narrative

With the freedom to step beyond the constraints imposed by pre-existing solutions—such as APIs,
libraries, or even legacy code—we open the door to reimagining how problems are formulated and
addressed in programming. This liberation allows us to focus not just on the mechanics of coding
but on the language we use to describe and engage with the core elements of our solutions. Among
these elements, *data* emerges as a focal point, often holding greater significance for the end user
than the specific implementation details of the code itself.

From the perspective of the customer or stakeholder, data is often the primary concern. It represents
the core value of a system--whether it's user behavior insights, financial metrics, or operational
analytics. Customers typically care less about the intricacies of the programming methods employed
and more about what the system achieves: the information it provides, the actions it enables, and
the outcomes it delivers.

This shift in perspective invites us to consider programming not just as an act of building systems,
but as a means of shaping a "language about data." Such a language focuses on how data is defined,
processed, and made accessible, rather than on the underlying code that supports these operations.
It bridges the gap between the technical realm of programming and the human-centered domain of
decision-making and value creation.


When I first began learning programming and working with computers, a piece of advice that was frequently
given was: *Is the problem you're trying to solve truly something that should be approached with a computer?*
This question forced us to pause and consider whether technology was the right tool for the task at hand,
or if there might be a simpler, more efficient way to address the issue without relying on machines.

In contrast, today the approach has shifted significantly. More often than not, we immediately introduce
technology without asking that critical question first. It's almost as if we automatically assume that the
solution to any problem must involve computers. This shift reflects a
*technological constraint in our thinking*--an assumption that technology is inherently the best or only
way to solve problems.

In many cases, this mindset may lead to over-engineering or solutions that are more complicated than necessary.
By skipping the important step of questioning whether technology is truly the most effective tool, we may 
overlook simpler, non-technological solutions or miss opportunities for more creative problem-solving approaches.
The tendency to view problems primarily through the lens of technology, rather than considering a broader
range of potential solutions, may be limiting in some contexts.

But when we *do* arrive at a computer solution, maybe we should approach it in another way than what is usual today?

To illustrate this, imagine a narrative in dialog form with two characters, Alex (the programmer) and
Taylor (the domain expert), collaborate to address a problem that initially isn't a straightforward coding
task. They approach the problem by reasoning about how to formulate it as a language.


### A Dialog on Solving Problems

__Scene__: *A small office with a whiteboard and a couple of laptops. Alex and Taylor sits at a desk, opposite each other.*

__Taylor__: Alex, I've been struggling with a way to handle biodiversity data for our conservation project.
We collect field data on species sightings, habitats, and environmental factors, but every project needs
something slightly different. It's chaos. I'd love to standardize how we work with this.

__Alex__: Hmm, sounds like a classic problem of managing variability. Tell me more—what do you need to do with the data?

__Taylor__: We need to describe observations: what species were seen, where, under what conditions. Then we
need to analyse trends, like how populations are changing over time. But the structure varies so much—sometimes
it's detailed, like "X species at Y latitude under Z temperature," and other times it's just "species spotted in this forest."

__Alex__: I see. You're essentially describing a system where the core problem is representing observations
and reasoning about them. Have you thought of it like a *language problem*?

__Taylor__: A language? Not really. I think of it as a database problem.

__Alex__: Databases store information, but you're asking for more. You want to describe your observations flexibly,
run analyses on them, and adapt as your research questions evolve. That's linguistic in nature-—you're trying to
express and manipulate ideas in a consistent way.

__Taylor__: Okay, so if this is a language problem, where do we start?

__Alex__: Let's start with the vocabulary. What are the essential concepts you deal with daily?

__Taylor__: Hmm. Definitely species, locations, dates, and environmental variables like temperature and humidity.
Also, things like interactions—predation or symbiosis, for example.

__Alex__: Great. So our language will need words for those concepts. Next, the grammar: How do these things relate
to each other? What's the smallest meaningful "sentence" you need to express?

__Taylor__: A single observation, like "Species A was seen at Location B on Date C under Condition D."
That's the basic unit of information.

__Alex__: Perfect. Now we need to decide how to formally represent that. Let's say we create a structure
for "observations," where each observation has slots for species, location, date, and conditions.
We could represent it in JSON for now:

```json
{
  "species": "A",
  "location": "B",
  "date": "C",
  "conditions": {"temperature": "20°C", "humidity": "80%"}
}
```

__Taylor__: That's simple and makes sense. But what about more complex cases? Like if we're observing multiple
species interacting or describing a habitat instead of a specific location?

__Alex__: That's where the language design gets fun. We can add layers of abstraction. For example, let's
make the concept of an "entity" flexible. An entity could be a species, a group of species, or a habitat.
Then interactions are just relationships between entities. For example:

```json
{
  "entities": [
    {"type": "species", "name": "A"},
    {"type": "species", "name": "B"}
  ],
  "relationship": "predation",
  "location": "B",
  "date": "C"
}
```

__Taylor__: That works! But now I'm wondering—how do we analyze this data? For example, trends over time?

__Alex__: Good question. This is where we define verbs or actions in our language. Think of them as ways
to manipulate or query your observations. For instance, "count occurrences of a species" or
"plot population trends over time." These can be operations in the language:

```json
{
  "operation": "count",
  "target": "species",
  "filter": {"name": "A", "date_range": ["2020-01-01", "2023-01-01"]}
}
```

__Taylor__: I like that. It's starting to feel like I could describe my research needs in terms of these
operations, almost like writing sentences in this language.

__Alex__: Exactly! Over time, we can add more expressive power, like creating reusable definitions or
models. For instance, if you're always grouping observations by habitat, you could define a "habitat observation" template.

__Taylor__: This makes so much sense now. It feels like I'm designing a language that lets me articulate
my scientific needs and then have the computer handle the rest.

__Alex__: That's the idea! You're no longer just "using software"--you're shaping a medium of expression
tailored to your domain. This way, the code isn't just solving problems; it's helping you think about problems.

__Taylor__: So in a way, we're creating a *scientific theory of observations*, but expressed *as a programming language*?

__Alex__: Exactly. And just like scientific theories, it's underdetermined by the data. You decide the structure
and rules that best capture the reality you're studying. Computers then become your tool for reasoning about and
exploring that model.

__Taylor__: This changes how I think about programming. It's not just about solving problems--it's about creating
ways to describe and explore them. Let's do it.



This dialog demonstrates how to shift from seeing a problem as something to "code" to viewing it as something
to "express" in a language. By iteratively building vocabulary, grammar, and semantics, Alex and Taylor create
a custom language that aligns with their problem, making it intuitive and flexible. This process mirrors how
scientific theories provide conceptual tools to understand and describe the world, much like a language
underdetermined by nature.
