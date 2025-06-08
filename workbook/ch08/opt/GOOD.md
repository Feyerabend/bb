
## Goodhart's Law

> *"When a measure becomes a target, it ceases to be a good measure."*
> Charles Goodhart, 1975

If you start optimising directly for a particular metric, that metric may
lose its original meaning or usefulness. The system adapts to game the metric
rather than genuinely improve the quality you're trying to capture.


### Simplified Examples

1. Programming/Software
- You use lines of code as a measure of developer productivity.
- Developers start writing longer, more verbose code to increase the count.
- Result: productivity appears to increase, but code quality degrades.

2. Machine Learning
- You optimise a model to maximize accuracy on the test set.
- The model overfits to the test data (or leaks data), boosting the metric but hurting generalization.
- Real-world performance degrades, even though the metric improves.

3. Web Optimisation
- A team is tasked with increasing click-through rate (CTR).
- They add clickbait headlines that increase CTR but reduce user trust and long-term engagement.


### Technical Interpretation in Algorithms

In systems where agents optimise an objective, Goodhart's Law warns:
- If you choose an imperfect proxy for your real goal (e.g. speed, quality, happiness), and optimise
  hard for it, agents may learn to exploit the proxy rather than solve the real problem.



### Variations / Related Principles

David Manheim and Scott Garrabrant identified four types of Goodhart effects:

__1. Regressional Goodhart__
- Optimising for an observed metric also amplifies noise and outliers.
- Example: Hiring only based on extremely high GPA leads to selecting outliers, not best candidates.

__2. Extremal Goodhart__
- In extreme ranges of the metric, the relationship with the true goal breaks down.
- Example: Pushing optimisation beyond training data makes the proxy invalid.

__3. Causal Goodhart__
- If the system misunderstands the causal relationship, optimising the metric may fail.
- Example: Giving everyone a stethoscope doesn't make them doctors.

__4. Adversarial Goodhart__
- When agents intentionally game the metric.
- Common in economic systems, KPIs, and AI safety discussions.


### Why It Matters in Programming and AI

- It warns you that blind optimisation of metrics (e.g. speed, test coverage, benchmark scores) can backfire.
- It relates to overfitting, reward hacking in reinforcement learning, and unintended consequences in algorithm design.
- In safety-critical AI, it's a foundational argument for needing alignment rather than naive optimisation.



### Summary

| Aspect           | Description                                                         |
|------------------|---------------------------------------------------------------------|
| Core idea        | Metrics lose meaning when targeted                                  |
| Domain relevance | Programming, AI, economics, policy                                  |
| Failure mode     | Optimising proxy instead of real goal                               |
| Examples         | LOC as productivity, CTR as success, accuracy as generalisation     |
| Defense          | Use multiple metrics, detect gaming, stay close to causal structure |


