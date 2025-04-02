
## The Monte Carlo Method

The Monte Carlo method is a computational technique that relies on random sampling
to approximate solutions to problems that might be deterministic in nature but are
too complex to solve directly. The method originated during the 1940s as part of the
Manhattan Project, where scientists, including Stanislaw Ulam and John von Neumann,
used it to model neutron diffusion in nuclear reactions. The name "Monte Carlo" was
inspired by the famous casino in Monaco, emphasising the role of randomness and
probability in the approach.

Monte Carlo methods are particularly useful for problems where an exact solution is
infeasible due to the problem's size, complexity, or the lack of a closed-form solution.
These methods excel in estimating numerical results when dealing with integration,
optimisation, and probability distribution sampling. They are widely used in physics,
finance, artificial intelligence, and engineering. A common application is numerical
integration, where direct analytical solutions are impractical, such as evaluating
integrals over high-dimensional spaces. Instead of solving them exactly, Monte Carlo
methods generate random samples and estimate the integral as an average over these
samples.

Another class of problems where Monte Carlo techniques prove effective is optimisation,
particularly in scenarios where deterministic algorithms struggle with local minima or
the sheer number of possible solutions. Simulated annealing, a Monte Carlo-based algorithm,
is often applied to combinatorial optimisation problems like the traveling salesman
problem, where a brute-force approach would be computationally prohibitive. Similarly,
in stochastic processes such as financial modelling, Monte Carlo simulations help predict
stock prices, assess risk, and model uncertainty in economic systems.

The defining characteristic of problems suited for Monte Carlo methods is their probabilistic
nature or the ability to be framed in terms of random sampling. These problems often involve
large search spaces, non-linear relationships, or chaotic behaviour, where deterministic
algorithms either fail or require excessive computation. While Monte Carlo simulations do
not always guarantee exact solutions, they provide statistically reliable approximations,
with accuracy improving as the number of samples increases. The trade-off between accuracy
and computational cost is one of the key considerations when applying the method.


### C Sample and Implementation

Sample run:

| Node        | 0   | 1   | 2     | 3   | 4   | 5   | 6   | 7   | 8   | 9     |
|-------------|-----|-----|-------|-----|-----|-----|-----|-----|-----|-------|
| 0           | INF | 4   | [5]   | INF | INF | INF | INF | INF | 5   | 7     |
| 1           | INF | INF | INF   | 8   | INF | 7   | INF | 5   | INF | INF   |
| 2           | INF | INF | INF   | INF | 5   | INF | INF | 3   | 8   | [1]   |
| 3           | INF | INF | INF   | INF | 10  | INF | INF | 6   | INF | INF   |
| 4           | 10  | INF | 7     | INF | INF | 9   | 2   | INF | INF | INF   |
| 5           | INF | INF | 9     | INF | 2   | INF | 4   | INF | INF | INF   |
| 6           | INF | 6   | 6     | INF | INF | INF | INF | INF | INF | INF   |
| 7           | 2   | INF | INF   | 7   | INF | INF | INF | INF | INF | INF   |
| 8           | INF | INF | INF   | INF | INF | 5   | INF | INF | INF | 5     |
| 9           | INF | INF | INF   | INF | 6   | 7   | 8   | INF | 3   | INF   |

The adjacency matrix represents the graph where each cell [i][j] shows
the weight (or distance) from node i to node j. "INF" means there's no 
irect connection between those nodes.
Looking at the best path found (0 -> 2 -> 9):

| From Node | To Node | Path Found       | Path Weight |
|-----------|---------|------------------|-------------|
| 0         | 9       | 0 -> 2 -> 9      | 6           |

Starting at node 0, the algorithm found a direct path to node 2 with weight
5 (visible in the first row, third column of the matrix).
From node 2, it found a direct path to the destination node 9 with weight 1
(visible in the third row, last column).
The total weight of this path is 5 + 1 = 6, which is shown as the estimated
shortest path distance.

This is actually an optimal solution for this particular graph, as it found
the minimum-weight path from node 0 to node 9. The Monte Carlo method was
successful here because:

- The graph is relatively small (10 nodes)
- The solution path is short (only 3 nodes)
- A large number of samples (10,000) were used

The randomised approach happened to find this optimal path through repeated
sampling and keeping track of the best result encountered.
