
## Other Topics in Computer Science

The *[Traveling Salesman Problem](./salesman/)* (TSP), *[Monte Carlo methods](./monte/)*, and
*Las Vegas algorithms* do not fit neatly into a structured format used for data structures and
their operations. They are fundamentally different in nature--TSP is a *problem*, while Mont
 Carlo and Las Vegas are *methods* (or classes of algorithms), making it difficult to categorise
 them in a table that expects specific time complexities and direct applications.


### Traveling Salesman Problem (TSP)

TSP is a combinatorial optimisation problem where the goal is to find the shortest possible route
that visits a set of cities exactly once and returns to the starting point. It does not describe
a specific algorithm but rather a challenge that needs solving. Various algorithms, such as
brute-force search, dynamic programming (Held-Karp), genetic algorithms, or simulated annealing,
can be used to approximate or exactly solve TSP.


### Monte Carlo Method

Monte Carlo is a probabilistic method, not a specific algorithm, that relies on randomness to
approximate solutions to computational problems. It is a broad approach used in numerical integration,
optimisation, and probabilistic modelling. In the context of TSP, Monte Carlo methods can be applied
in heuristic search techniques, such as randomised tour sampling or simulated annealing, where
random modifications to a solution help explore the search space efficiently.

Monte Carlo algorithms are characterised by their use of randomness to obtain approximate solutions.
They may not always produce the correct answer, but they provide probabilistic guarantees about the
accuracy of their results. The trade-off is between computational efficiency and solution precision.


### Las Vegas Algorithms

Las Vegas algorithms represent another class of randomised algorithms that differ fundamentally from
Monte Carlo methods. While Monte Carlo algorithms may produce incorrect results with some probability,
Las Vegas algorithms always produce correct results but have variable (random) execution times. The
randomness in Las Vegas algorithms is used to improve average-case performance rather than to approximate
solutions.

Key characteristics of Las Vegas algorithms include:

- *Guaranteed correctness*: Unlike Monte Carlo methods, Las Vegas algorithms always return the correct answer
- *Variable runtime*: The execution time depends on random choices made during computation, but the expected
  runtime is typically efficient  
- *Theoretical possibility of non-termination*: While extremely unlikely in practice, some Las Vegas algorithms
  might theoretically run indefinitely

Common examples of Las Vegas algorithms include:

- *Randomised QuickSort*: Uses random pivot selection to avoid worst-case O(n²) behaviour on already-sorted arrays,
  maintaining O(n log n) expected time complexity
- *Randomised Binary Search variants*: Employ random selection strategies while preserving correctness
- *Random sampling algorithms*: Such as reservoir sampling or Fisher-Yates shuffle for selecting random subsets
- *Randomised primality testing*: Algorithms like Miller-Rabin that can definitively prove compositeness but use
  randomisation for efficiency

Las Vegas algorithms are particularly valuable in scenarios where correctness is paramount but improved average
performance is desired. They are often preferred over their deterministic counterparts when the worst-case inputs
are likely to occur in practice.


### Table

| Name  | Type   | Complexity    | Usage  |
|-------|--------|---------------|---------|
| Traveling Salesman Problem (TSP) | Combinatorial Optimisation Problem | NP-hard (cf. [P vs NP](./../limits/PvsNP.md)) | Route optimisation, logistics, circuit design |
| Monte Carlo Method | Probabilistic Computational Method | Varies (depends on sampling iterations) | Simulation, numerical integration, optimisation |
| Las Vegas Algorithms | Randomised Algorithmic Method | Variable runtime, correct results | Sorting, searching, sampling, primality testing |
