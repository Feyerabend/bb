
## Markov Chains

These are the most basic type of Markov model.
- A Markov Chain is a stochastic process over a discrete set of states.
- It satisfies the Markov property.
- It is memoryless: the next state depends only on the current one.
- Used in: weather prediction, queueing theory, genetics, text generation (e.g., Markov text models), etc.
- Can be extended with transition matrices, stationary distributions, absorbing states, etc.


### Definition

Markov Chains are stochastic processes modeling sequences of events where the next
state depends only on the current state, embodying the memoryless Markov property:
```math
P(X_{n+1} = x_{n+1} \mid X_n = x_n, \dots, X_1 = x_1) = P(X_{n+1} = x_{n+1} \mid X_n = x_n)
```
They operate in discrete-time (DTMCs) or continuous-time (CTMCs),
with states transitioning based on probabilities.


### Properties

*Transition Matrix.* An $n \times n$ matrix $P$ where $P_{ij}$ is the probability of moving from
state $i$ to state $j$. Each row sums to 1.

*Stationary Distribution.* A probability vector $\pi$ where $\pi = \pi P$, representing long-term
state probabilities for ergodic chains.

*Ergodicity.* Chains that are irreducible (all states reachable) and aperiodic (no fixed cycles)
converge to a unique stationary distribution.

*Recurrence.* States are recurrent if the chain returns to them with probability 1; otherwise,
they are transient.

*Absorbing States.* States with no outgoing transitions, trapping the chain once entered.


### Examples

- Weather Model: States: Sunny, Rainy. Transition example: 70% chance of Sunny tomorrow if Sunny today.
- Random Walk: Moving left or right on a number line with equal probability, a classic memoryless process.
- PageRank: Web pages as states, transitions via hyperlinks, with ranks derived from the stationary distribution.


### Applications

Markov Chains are widely used in:

- Finance: Modeling stock prices or credit ratings.
- Biology: Analyzing DNA sequences.
- Computer Science: Powering algorithms like PageRank and Hidden Markov Models for speech recognition.
- Physics: Markov Chain Monte Carlo for complex simulations.
- Economics and Sports: Modeling business cycles or game strategies.


### Mathematical Dynamics

The state distribution evolves as $\pi_t = \pi_0 P^t$, where $\pi_0$ is the initial distribution and
$P$ is the transition matrix. Ergodic chains converge to a stationary distribution as $t \to \infty$.


### Transition to Statistical Learning

While Markov chains originate from traditional probabilistic modeling and are often used in explicitly
defined simulation-based or rule-based systems, they also form the foundation for data-driven models
that learn from experience or observation. This transition into learning marks their relevance in *machine
learning*. What we will explore in more detail in the following chapter [ch08](./../../../ch08/ai/ml/).

When the transition matrix is estimated from data rather than hardcoded, the system is no longer just
executing a fixed algorithm but adapting to patterns discovered in the input data. This estimation
process, often via maximum likelihood or Bayesian inference, aligns Markov chains with statistical
learning methods.

Markov chains also underpin Hidden Markov Models (HMMs), which are widely used in speech recognition,
natural language processing, and bioinformatics. Here, hidden variables and inference algorithms such
as the Forward-Backward or Viterbi algorithm are used--clearly statistical and ML-oriented techniques.

Moreover, in reinforcement learning, Markov Decision Processes (MDPs) extend the Markov framework by
associating states with actions and rewards, enabling agents to learn policies that maximize expected
return. These models are often learned or optimized from data and simulations, further embedding Markov
structures in the core of machine learning.

Thus, although Markov chains begin in the realm of classical, analytical modeling, their principles
provide essential scaffolding for modern statistical AI. The moment a model starts learning its structure
or estimating parameters from data, it crosses into the statistical learning regime, even when the
underlying mechanics remain grounded in the traditional Markov framework.

The transition from predefined probabilistic systems to learned, adaptive ones is the conceptual shift
where Markov chains become part of the machine learning landscape.
