
## Other Topics in Computer Science

The *[Traveling Salesman Problem](./salesman/)* (TSP) and
*[Monte Carlo methods](./monte/)* do not fit neatly into a structured format used for
data structures and their operations. They are fundamentally different in nature--TSP
is a *problem*, while Monte Carlo is a *method* (or a class of algorithms), making it
difficult to categorise them in a table that expects specific time complexities and
direct applications.


### Traveling Salesman Problem (TSP)

TSP is a combinatorial optimisation problem where the goal is to find the shortest possible
route that visits a set of cities exactly once and returns to the starting point. It does
not describe a specific algorithm but rather a challenge that needs solving. Various algorithms,
such as brute-force search, dynamic programming (Held-Karp), genetic algorithms, or simulated
annealing, can be used to approximate or exactly solve TSP.


### Monte Carlo Method

Monte Carlo is a probabilistic method, not a specific algorithm, that relies on randomness to
approximate solutions to computational problems. It is a broad approach used in numerical
integration, optimisation, and probabilistic modelling. In the context of TSP, Monte Carlo
methods can be applied in heuristic search techniques, such as randomised tour sampling or
simulated annealing, where random modifications to a solution help explore the search space
efficiently.

| Name  | Type   | Complexity    | Usage  |
|--|--|--|--|
| Traveling Salesman Problem (TSP) | Combinatorial Optimisation Problem | NP-hard (cf. [P vs NP](./../limits/PvsNP.md)) | Route optimisation, logistics, circuit design |
| Monte Carlo Method | Probabilistic Computational Method | Varies (depends on sampling iterations) | Simulation, numerical integration, optimisation |
