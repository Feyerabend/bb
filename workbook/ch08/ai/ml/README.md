
## What is Machine Learning (ML)?

The story of machine learning (ML) in AI begins as a divergence from what is often called [GOFAI](./../gofai/)
(Good Old-Fashioned Artificial Intelligence), which dominated from the 1950s through the 1980s. GOFAI relied
on symbolic reasoning, logic, and handcrafted rules to simulate intelligent behavior. Researchers built expert
systems and used formal languages to model human reasoning. These systems worked well in constrained domains
(like theorem proving or medical diagnosis) but struggled with uncertainty, noise, and learning from data.

By the 1980s, limitations of GOFAI became clear. Systems required enormous manual effort and lacked adaptability.
At the same time, researchers in statistics and pattern recognition—fields somewhat separate from mainstream
AI—were exploring probabilistic methods and data-driven learning. Techniques like decision trees, nearest
neighbor methods, and early neural networks were gaining traction. These methods could learn patterns from
data without needing explicit programming of rules.

The 1990s saw a growing convergence between AI and statistical learning, sometimes called the "statistical
revolution" in AI. Developments included:
- Bayesian networks (e.g., Judea Pearl’s work),
- Support Vector Machines (SVMs),
- boosting algorithms, and
- the broader framework of probabilistic inference and optimisation.

At this point, machine learning started to dominate practical AI applications—such as speech recognition,
handwriting recognition, and web search. GOFAI faded from the center of research as its systems could not
scale or adapt as well as ML-based approaches.

The major turning point came in the 2010s, with the resurgence of neural networks under the name deep
learning, thanks to increased computational power (GPUs), large datasets, and algorithmic innovations
(like better training methods and architectures). Models like AlexNet (2012) showcased the power of deep
neural networks in tasks like image recognition, kicking off an era where learning from data replaced
rule-based reasoning as the primary method of building intelligent systems.

Today, machine learning—especially deep learning—is the dominant approach in AI. However, there is a
growing recognition that symbolic reasoning and ML might need to be integrated, leading to hybrid approaches
that combine structured knowledge and statistical learning, aiming to recapture the generality and
abstraction GOFAI once sought but with the adaptability of modern ML.


### The Concepts

So, Machine Learning (ML) is a paradigm where computers learn rules or patterns directly from data rather
than being explicitly programmed with them. Instead of providing the computer with a set of rigid if/else
statements or fixed algorithms, you supply it with *data* and *examples of the desired output for that data*.
The machine then analyses these examples to discover underlying patterns, forming a "model" that can be
used to make predictions or decisions on new, unseen data.

Think of it this way:

* *Conventional Programming.* You, the programmer, define the Rules that process Data to produce Answers.
  For instance, you might write code that specifies exactly how to calculate a tax based on income brackets.  
* *Machine Learning.* You provide Data along with the Answers (or labels) for that data, and the computer's
  algorithms work to learn the Rules (which collectively form a "model"). An example is feeding an ML
  system thousands of images of cats and dogs, each labeled correctly. The system learns to identify
  features that distinguish cats from dogs without being explicitly told "a cat has pointy ears and whiskers."

For example, to classify emails as "spam" or "not spam" in ML, you would feed an algorithm thousands of
pre-labeled emails (e.g., "This email about a 'Nigerian prince' is spam," "This email from my colleague
is not spam"). The algorithm then identifies patterns (e.g., specific word frequencies like "urgent" or
"free," sender characteristics, formatting) that differentiate spam from legitimate emails. Once trained,
this learned "model" can then predict whether a *new, unseen* email is spam or not with a certain degree
of accuracy.


### ML vs. Conventional Programming: Shifting Mindsets

The biggest shift from conventional programming to ML is the fundamental change in how solutions are developed:
the transition from explicit rules to data-driven discovery of rules.

In conventional programming, you define precise, step-by-step instructions for the computer to execute:

```python
def classify_email_conventional(email_text):  
    if "nigerian prince" in email_text.lower() and "urgent" in email_text.lower():  
        return "spam"  
    elif "free lottery" in email_text.lower() or "click here" in email_text.lower():  
        return "spam"  
    else:  
        return "not spam"
```

This approach is highly effective when the rules governing a problem are clear, finite, and easily expressible
by a human. However, ML truly excels when these rules are too complex, too numerous, constantly changing, or
even impossible for a human to articulate explicitly. For instance, how would you write if/else statements to
reliably recognize a human face in an image, accounting for different angles, lighting, and expressions?

This is where the ML mindset comes into play:

* You don't tell the machine *how* to classify spam; you show it *what* spam looks like through numerous examples.
  The machine then figures out the how.  
* You don't program the formula for recognizing faces; you provide many examples of faces and non-faces. The
  machine then identifies the intricate patterns that define a face.

This paradigm shift enables the solution of problems that are otherwise intractable with traditional programming,
especially  those involving complex, nuanced patterns in large datasets, such as image recognition, natural language
processing, and personalized recommendations.

For a mathematical introduction to some core machine learning concepts from a conventional programmer's standpoint,
see [MATH.md](./MATH.md).


### A General Observation: Traditional Programming vs. Machine Learning

To reiterate the core distinction:

* *Traditional Programming.* You explicitly define the rules (algorithms, logic) that operate on given data to produce
  answers. The flow is `Rules + Data -> Answers`.  
* *Machine Learning.* You provide data along with the answers (labels or outcomes), and the system then learns the
  rules (i.e., constructs a model) that connect the data to those answers. The flow is `Data + Answers -> Rules (Model)`.

This fundamental difference allows ML to tackle problems where the underlying rules are either unknown, too complex to
define manually, or constantly evolving. By leveraging patterns discovered from vast amounts of data, ML systems can
achieve remarkable capabilities in areas like pattern recognition, prediction, and decision-making that are beyond the
scope of traditional rule-based programming.

*Continue learning the [core](./CORE.md) of ML ..*
