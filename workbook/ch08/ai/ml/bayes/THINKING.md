
## "Bayesian Thinking"

Bayes theorem,

```math
P(H|E) = \frac{P(E|H) \cdot P(H)}{P(E)}
```

is not only a tool for predicting outcomes, but also a model for reasoning itself. In a broader sense,
it offers a framework for how beliefs should be updated in light of new evidence. This way of thinking
has implications far beyond statistics--including in how we reason, make decisions, and even how we
approach programming.

As machine learning becomes increasingly central to programming practice, understanding both the theory
and application of Bayesian reasoning can offer a fresh perspective. It encourages us to move away from
rigid, black-and-white thinking and instead embrace uncertainty, iteration, and revision. This contrasts
sharply with the more fixed, intuitive modes of thought common in everyday life and communication.

Thinking in Bayesian terms fundamentally alters how we deal with uncertainty, incorporate information,
and evaluate choices. While "ordinary" thinking often rests on fixed beliefs or instincts, Bayesian
reasoning treats beliefs as provisional--updated continuously as new data arrives. 


### Belief Representation

Normal Thinking
- Beliefs are often binary or static: "X is true" or "X is false".
- People rely on heuristics (rules of thumb), such as representativeness, availability, or confirmation bias.
- Certainty is often overestimated.

Bayesian Thinking
- Beliefs are represented probabilistically: "There's a 70% chance X is true."
- All beliefs are provisional and can be updated.
- Uncertainty is explicitly modeled and accepted as part of reasoning.



### Learning from New Evidence

Normal Thinking
- New evidence may be ignored if it contradicts prior belief (confirmation bias).
- People often change beliefs only when evidence is overwhelming or emotionally charged.
- Updates tend to be all-or-nothing: either reject or accept new claims.

Bayesian Thinking
- New evidence modifies the strength of belief through Bayes' Theorem:

```math
P(H|E) = \frac{P(E|H) \cdot P(H)}{P(E)}
```

Where:
- $H$ = hypothesis
- $E$ = evidence
- $P(H|E)$ = updated belief (posterior)
- $P(H)$ = prior belief
- $P(E|H)$ = likelihood of evidence if hypothesis is true

- Even weak evidence has some influence, gradually refining beliefs.



### Decision Making

Normal Thinking
- Decisions are often made using gut instinct, emotion, or social influence.
- Risk is often misunderstood or misrepresented.
- Optimism bias or fear may skew perceived outcomes.

Bayesian Thinking
- Decisions are made using expected utility: weigh outcomes by their probabilities and consequences.
- Tradeoffs are analyzed probabilistically.
- Risk and uncertainty are part of the decision, not noise to be ignored.



### Cognitive Consequences

Normal Thinking
- Susceptible to:
    - Anchoring
    - Belief perseverance
    - Motivated reasoning
    - Poor at dealing with rare events or probabilistic chains (e.g., conjunction fallacy).

Bayesian Thinking
- Promotes:
    - Openness to updating
    - Tolerance of uncertainty
    - Rational integration of new data

But:
- Computationally intensive
- Requires explicit modeling of priors and likelihoods
- Can seem counterintuitive in everyday life



### Examples

Medical Diagnosis  
- Normal thinking: "The test is positive, so I probably have the disease."  
- Bayesian thinking: "What's the base rate of the disease? How accurate is the test? Let me update my belief accordingly."

Judging Claims  
- Normal thinking: "I saw a video; it must be true."  
- Bayesian thinking: "How likely is this video to exist under different hypotheses? What's the prior likelihood?"

Legal Reasoning  
- Normal thinking: "The suspect has no alibi, so they must be guilty."  
- Bayesian thinking: "How likely is it that an innocent person would lack an alibi? What prior probability do we assign to guilt before the evidence?"

Scientific Discovery  
- Normal thinking: "This experiment confirms the theory, so the theory is true."  
- Bayesian thinking: "How surprising is this result if the theory were false? How does this update our confidence in the theory compared to competing ones?"

Risk Assessment  
- Normal thinking: "It hasn’t happened before, so it probably won’t happen."  
- Bayesian thinking: "Even if something hasn't happened yet, rare events still have a probability. Let's estimate it based on indirect evidence and update over time."

Economics and Forecasting  
- Normal thinking: "The market is crashing; everything is doomed."  
- Bayesian thinking: "Given past data and external conditions, how likely is a full collapse? Let’s adjust our expectations as more signals appear."

Programming and Debugging  
- Normal thinking: "It worked yesterday, so the bug must be in the new code."  
- Bayesian thinking: "What’s the likelihood the bug is in the new code vs. an unnoticed earlier issue? How should I revise my hypothesis as I test each possibility?"

Machine Learning and Model Evaluation  
- Normal thinking: "My model performs well on the test set, so it’s reliable."  
- Bayesian thinking: "Given the size and variability of the data, and potential overfitting, how confident should I really be? What’s the probability this model generalizes well?"

Software Design  
- Normal thinking: "This feature is rarely used, so optimising it isn’t worth the time."  
- Bayesian thinking: "Given low usage now but potential future growth or edge cases, what’s the expected value of optimising this path? Can we update this belief with telemetry data?"



### Consequences

For Individuals:
- More calibrated beliefs
- Better long-term decision making
- Less swayed by noise or manipulation

For Society:
- Encourages evidence-based policy
- Reduces extremism by softening belief rigidity
- Improves scientific reasoning and forecasting



### Summary

| Aspect          | Normal Thinking                      | Bayesian Thinking                           |
|-----------------|--------------------------------------|---------------------------------------------|
| Beliefs         | Binary or vague                      | Probabilistic                               |
| Evidence        | Often filtered or ignored            | Systematically updates beliefs              |
| Decision-making | Heuristic/emotional                  | Rational, expectation-based                 |
| Flexibility     | Resistant to change                  | Encourages continuous refinement            |
| Risk handling   | Prone to misjudgment                 | Explicitly modeled                          |


Perhaps, if we all thought a bit more like Bayesians, we'd likely be more humble, more curious, and less
dogmatic--but also more cognitively taxed. The cost is complexity; the benefit is accuracy.

