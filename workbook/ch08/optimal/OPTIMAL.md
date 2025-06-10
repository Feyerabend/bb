
## Optimisation

Optimisation, in its broadest sense, is the pursuit of the best possible outcome given a
set of constraints. While often framed in mathematical and computational terms, the concept
has deep philosophical roots, touching on ideas of efficiency, trade-offs, and even human
decision-making.

At its core, optimisation reflects a fundamental tension between perfection and practicality.
In philosophy, this relates to the *ideal* vs. *the real*--we may strive for the best, but
constraints (whether physical, logical, or ethical) often force us to settle for something
less than perfect. This mirrors the idea in engineering and science that optimisation is
rarely about finding a single, absolute best solution but rather the best possible one given
limited resources.

Another philosophical aspect of optimisation is goal-setting and values. What does it mean
to "optimise" something? The answer depends entirely on what we consider valuable. In economics,
it might mean maximising wealth; in ethics, it could mean maximising happiness (utilitarianism);
in AI, it might mean optimising for accuracy, fairness, or interpretability. This subjectivity
means that optimisation is always tied to deeper philosophical questions about what we should
strive for.

Furthermore, optimisation involves trade-offs-the recognition that improving one aspect of a
system often comes at the cost of another. This resonates with ethical dilemmas, such as the
trolley problem, where choosing the optimal outcome involves weighing different kinds of harm.
In economics and environmental science, this appears in the form of Pareto efficiency, where
an optimal state is reached when no further improvements can be made without making something
else worse.

Finally, there is a teleological perspective: the idea that all systems, whether biological,
social, or artificial, evolve toward some form of optimisation. Evolution itself can be seen
as an optimisation process, refining species over time through natural selection. In human
systems, markets, technologies, and even moral frameworks evolve through a similar process,
constantly seeking better solutions to emerging challenges.

Ultimately, optimisation is not just a mathematical tool-it is a way of thinking about problems,
balancing competing priorities, and navigating the complexities of life itself. It asks us to
confront limits, define what we value, and acknowledge that "the best" is often a moving target,
shaped by context and perspective.



## Optimisation in Practice

Optimisation is a fundamental principle in many scientific and engineering disciplines,
aiming to find the best possible outcome under given constraints. At its core, optimisation
involves either maximisation (e.g., profit, utility, reward) or minimisation (e.g., cost,
loss, risk). Despite differences in formulation, the underlying mathematical and computational
techniques often share common ground across fields.

From control systems to economics, artificial intelligence, and statistical learning,
optimisation serves as a unifying framework for decision-making. Each field adapts the
concept based on its unique goals, constraints, and methodologies.


### Applications Across Domains


__1. Control Systems: Precision and Stability__

Control theory is widely used in robotics, aerospace, and industrial automation, where
minimising a cost function ensures system stability and efficiency. Examples include:
- Self-driving cars adjusting speed and steering to minimise deviation from an optimal trajectory.
- Flight control systems optimising thrust and aerodynamic forces to maintain stability.
- Energy grids minimising power loss while ensuring demand is met efficiently.

These systems often rely on techniques like PID controllers, Kalman filters, and model predictive
control (MPC) to optimise real-time decision-making.

- Mathematical Perspective: A common formulation is in optimal control theory, where
  we define a function $J(x, u)$ (cost function), and we seek to minimise:
```math
  J = \int_0^T L(x(t), u(t)) dt + \Phi(x(T))
```
  where $x(t)$ is the system state, $u(t)$ is the control input, $L(x,u)$ is the running cost,
  and $\Phi(x(T))$ is the terminal cost.



__2. Economics: Decision-Making at Scale__

Optimisation plays a crucial role in individual, corporate, and societal decision-making.
- Consumers maximise utility when choosing goods under budget constraints.
- Firms optimise production levels to maximise profits while managing costs.
- Governments design policies to optimise economic welfare, balancing equity and efficiency.

Methods like game theory, linear programming, and behavioural economics models help solve
complex economic optimisation problems.

- Organisations (firms) maximise profit, defined as revenue minus costs.
Example: A firm seeks to maximise its profit function:
```math
\max_{Q} \quad \pi = P(Q) \cdot Q - C(Q)
```
where $P(Q)$ is the demand function, or explicitly over price and quantity subject
to the demand constraint.

- Mathematical Perspective: In game theory and microeconomics, utility functions measure
preference over outcomes. A social welfare function aggregates individual utilities:
```math
W(U_1, U_2, …, U_n)
```
where $U_i$ is the utility of individual $i$, and different formulations (e.g., Pareto
efficiency, Rawlsian max-min fairness) lead to different solutions.



__3. Artificial Intelligence: Learning and Adaptation__

Many AI techniques revolve around maximising rewards or minimising loss.
- Reinforcement Learning (RL): Used in robotics, game AI (e.g., AlphaGo), and autonomous
  systems where agents learn optimal strategies by maximising cumulative rewards.
- Neural Network Training: Deep learning models minimise loss functions to improve accuracy,
  using gradient-based optimisation methods like SGD (stochastic gradient descent).
- Search and Planning: AI algorithms optimise search paths in applications such as route
  planning (Google Maps), supply chain logistics, and recommendation systems.

Example: In reinforcement learning (RL), an agent interacts with an environment and selects
actions to maximise future expected rewards.
- Mathematical Perspective: The optimisation problem in RL is formulated using the Bellman equation:
```math
V(s) = \max_a \sum_{s{\prime}} P(s{\prime} | s, a) \left[ R(s, a) + \gamma V(s{\prime}) \right]
```
where $V(s)$ is the value function, $P(s{\prime} | s, a)$ is the transition probability, $R(s, a)$
is the reward, and $\gamma$ is a discount factor.



__4. Statistical Learning and Decision Theory__

Statistical methods focus on minimising the expected error to improve predictions and decisions
under uncertainty.
- Machine Learning: Supervised models optimise loss functions (e.g., cross-entropy for classification,
  MSE for regression).
- Bayesian Decision Theory: Optimises decision-making under probabilistic uncertainty, crucial in
  medical diagnosis, financial risk analysis, and automated trading.
- Experimental Design: Ensures efficient data collection in fields like drug development and
  industrial process optimisation.

- Example: In supervised learning, given input x and true output y, a model produces a prediction
  $f(x)$. A loss function $L(y, f(x))$ measures the error, and the goal is to minimise the expected loss:
```math
\min_f \mathbb{E}_{(x,y) \sim P} [ L(y, f(x)) ]
```
- Common Loss Functions:
- Mean Squared Error (MSE) for regression:
```math
L(y, f(x)) = (y - f(x))^2
```
- Cross-entropy loss for classification:
```math
L(y, f(x)) = - \sum y_i \log f(x_i)
```

### Complementary Areas and Broader Perspectives

Optimisation interacts with various fields that extend its principles:
- Operations Research (OR): Focuses on large-scale decision-making, including supply chain management,
  logistics, and manufacturing optimisation.
- Information Theory: Optimises data compression and transmission, crucial in networking, cryptography,
  and communications.
- Computational Complexity: Studies the efficiency of optimisation algorithms, influencing areas like
  the P vs. NP problem and algorithmic game theory.
- Systems Biology: Uses optimisation to model biological networks, enzyme pathways, and genetic evolution.

Across all these domains, convex optimisation, dynamic programming, evolutionary algorithms, and Monte Carlo
methods provide powerful tools to tackle real-world optimisation challenges.



### Common Theme: Optimisation Across Domains

The core idea across all these fields is optimisation, but different domains frame it as maximisation or minimisation:

| Field           | Objective                       | Function Type   |
|-----------------|---------------------------------|-----------------|
| Control Systems | Minimise cost function          | $J(x, u)$         |
| Economics       | Maximise utility/profit/welfare | $U(x), π(x)$      |
| Research (AI)   | Maximise expected rewards       | $V(s)$ (Bellman)  |
| Statistics/ML   | Minimise expected loss          | $𝔼[L(y, f(x))]$   |

- Duality: Many problems can be framed in both ways. For example, maximising rewards is equivalent
  to minimising negative rewards.

- Connections: Economic models influence machine learning (e.g., multi-agent reinforcement learning).
  Statistical learning theory underpins AI algorithms.


### Projects

1. The Trade-Off Simulator: Develop a simple interactive program that demonstrates the trade-offs
   in optimisation problems. For example, a web-based tool where users adjust parameters (e.g.,
   speed vs. energy consumption in a self-driving car) and see how optimising for one affects the others.

2. Resource-Constrained AI Training: Implement a simple neural network that can only be trained
   with limited computational resources (e.g., a fixed number of floating-point operations).
   Investigate how different optimisation techniques (gradient clipping, learning rate scheduling,
   weight quantisation) affect the final model performance.

3. Evolutionary Algorithm for Problem-Solving: Write a genetic algorithm that optimises a complex
   function (e.g., traveling salesman problem, game AI, or image compression). Reflect on how
   evolutionary principles like mutation and selection contribute to optimisation.

4. Ethical Optimisation in AI: Build a decision-making AI (e.g., a reinforcement learning agent)
   and implement different reward structures. Compare the outcomes when optimising for different
   values (e.g., individual gain vs. collective welfare). How does the chosen objective shape the
   behaviour of the AI?

5. Real-Time Control System: Implement a PID controller in a small robotic simulation or an interactive
   program. Optimise for stability and response time, and analyse how tuning the parameters affects
   the outcome.

6. Game Theory and Competitive Optimisation: Simulate an economic system with multiple agents trying
   to maximise their own rewards while competing for shared resources. Explore the Nash equilibrium
   and Pareto efficiency in different scenarios.

7. Energy-Efficient Computing: Optimise a computational task (e.g., matrix multiplication, sorting)
   to reduce energy consumption. Compare different algorithms and hardware-level optimisations
   (e.g., parallel processing, lower precision computation).

8. Multi-Objective Optimisation: Implement an optimisation algorithm that must balance multiple
   competing objectives (e.g., a web server that must optimise both speed and security, or a route
   planner that minimises both time and fuel consumption).

9. AI Fairness and Bias in Optimisation: Train an AI model with different fairness constraints
   (e.g., balancing accuracy across different groups). Explore how optimising for fairness can
   conflict with optimising for accuracy.

10. Compression and Information Theory: Implement a simple data compression algorithm and analyse
    the trade-off between compression ratio and loss of information. Compare entropy-based methods
    with lossy and lossless techniques.

11. Dynamic Programming Challenge: Solve a classic dynamic programming problem (e.g., knapsack problem,
    shortest path) and analyse the time-space trade-off of memoization.

12. Optimisation in Programming Languages: Write a simple compiler optimisation pass that transforms
    inefficient code into a more optimised form (e.g., constant folding, loop unrolling).

13. Interactive Visualisation of Optimisation Algorithms: Create a visualisation tool that shows how
    different optimisation techniques (gradient descent, simulated annealing, genetic algorithms)
    solve the same problem in different ways.

14. Reinforcement Learning in Games: Implement a basic AI that learns to play a simple game (e.g.,
    tic-tac-toe, a small grid-world environment) using Q-learning or deep reinforcement learning.
    Experiment with different reward structures.

15. Constraint Satisfaction Problems: Implement a constraint solver for a problem like Sudoku or
    scheduling, exploring how different heuristics improve performance.

