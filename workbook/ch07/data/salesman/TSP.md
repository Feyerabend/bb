
## The Traveling Salesman Problem

The Travelling Salesman Problem (TSP) asks the following: given a set of cities and
the distances between every pair of them, find the shortest possible route that visits
each city exactly once and returns to the starting city. The problem is simple to
state but difficult to solve efficiently. A solution is not just any tour that covers
all cities, but the one whose total distance (or cost) is minimal among all such tours.
The input is typically represented as a complete weighted graph, where cities are
nodes and distances are edge weights, and the task is to find a minimum-weight
Hamiltonian cycle.

What makes the TSP important is that the number of possible tours grows factorially
with the number of cities. For even moderate sizes, exhaustive search becomes
computationally infeasible. This places the TSP among the classic NP-hard problems
in computer science and optimisation. It serves as a benchmark for algorithms,
heuristics, and approximation methods, and it captures a central tension in computation:
problems that are easy to define and verify, but extraordinarily hard to solve optimally at scale.

TSP is one of the most famous *problems* in computational mathematics and optimisation,
with roots tracing back to the 1800s. The problem was first mathematically formulated
by Irish mathematician W.R. Hamilton and British mathematician Thomas Kirkman.
Later in the 1930s, Karl Menger of the Vienna Circle provided the formalisation
recognised today. During the 1950s and 60s, researchers at the RAND Corporation--including
George Dantzig, Ray Fulkerson, and Selmer Johnson--achieved a breakthrough by solving a
49-city instance, a remarkable feat for the era. In 1972, Richard Karp demonstrated the
NP-hard nature of TSP, explaining why large-scale exact solutions remain computationally
challenging. Beyond theoretical significance, TSP has practical applications in logistics,
manufacturing (e.g., circuit board drilling), DNA sequencing, and astronomy (e.g.,
telescope observation scheduling).


### Approaches to Solving TSP

Over decades, diverse strategies have emerged to tackle TSP. Exact algorithms include
methods like *Branch and Bound* from the 1960s, which systematically eliminates subsets
of solutions, and the Held-Karp dynamic programming algorithm (1962) with O(n²2ⁿ)
complexity. Integer linear programming approaches using cutting plane methods were
pioneered by Dantzig, Fulkerson, and Johnson. Approximation algorithms offer near-optimal
solutions, such as the Christofides Algorithm (1976), which guarantees solutions within
1.5 times the optimal length, and minimum spanning tree (MST)-based methods. Heuristic
approaches range from simple greedy methods like *Nearest Neighbour* to sophisticated
local search techniques such as 2-opt, 3-opt, and the Lin-Kernighan Algorithm (1973).
Metaheuristics draw inspiration from natural processes, including simulated annealing
(metallurgy), ant colony optimisation (ant foraging), and genetic algorithms (natural
selection), which gained prominence in the 1980s.


### Genetic Algorithm Approach

The genetic algorithm for TSP builds on principles developed by researchers like David
Goldberg and John Holland in the 1980s-90s. A typical implementation:


#### City Generation and Distance Calculation

```python
def generate_cities(num_cities, seed=42):
    random.seed(seed)
    return [(random.randint(0, 100), random.randint(0, 100)) for _ in range(num_cities)]

def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)
```

This code generates a Euclidean TSP instance with cities as 2D points. Using a fixed
seed ensures reproducibility, critical for benchmarking and debugging.


#### Population Initialisation

```python
def create_population(size, num_cities):
    return [random.sample(range(num_cities), num_cities) for _ in range(size)]
```

Random permutations create a diverse initial population, essential for exploring the
vast solution space of TSP.


#### Selection Mechanism

```python
def select_parents(population, cities):
    tournament_size = 5
    selected = random.sample(population, tournament_size)
    return min(selected, key=lambda route: route_length(route, cities))
```

Tournament selection balances selection pressure and diversity. A tournament size of
5 provides moderate pressure while maintaining genetic variety.


#### Crossover Operation

```python
def crossover(parent1, parent2):
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end] = parent1[start:end]
    p2_index = 0
    for i in range(size):
        if child[i] == -1:
            while parent2[p2_index] in child:
                p2_index += 1
            child[i] = parent2[p2_index]
    return child
```

Ordered Crossover (OX), introduced by Davis in 1985, preserves parent order and
ensures valid permutations by filling gaps with unused cities.


#### Mutation

```python
def mutate(route, mutation_rate=0.1):
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route
```

Swap mutation maintains permutation validity. A 0.1 mutation rate encourages diversity
without overwhelming existing solutions.


### Enhancement Opportunities

Several improvements could elevate the algorithm's performance. *Elitism*--preserving top
solutions across generations--prevents loss of high-quality routes. *Edge Recombination Crossover*,
designed by Whitley et al. in 1989, prioritises edge preservation between cities over
positional inheritance. Integrating local search techniques like 2-opt or 3-opt post-crossover/mutation
transforms the approach into a memetic algorithm, combining genetic and local optimisation.
Adaptive parameters that adjust mutation rates based on population diversity can dynamically
balance exploration and exploitation. Finally, island models, where multiple sub-populations
evolve independently with occasional migration, may enhance solution quality through parallel
exploration.

This implementation captures core principles of genetic algorithms for TSP, continuing a rich
tradition of computational problem-solving. By incorporating modern enhancements, it can
further bridge historical methodologies with contemporary optimisation challenges.

