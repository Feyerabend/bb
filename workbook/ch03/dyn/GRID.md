
## State DP

> [!IMPORTANT]  
> To fully understand the concepts in this text, readers would preferably need some background in:
> Mathematics (particularly linear algebra and calculus),
> Statistics and probability,
> Machine learning fundamentals,
> Basic neural network concepts,
> Reinforcement learning principles,
> Dynamic programming concepts,
> Optimisation theory.
> Without this foundation, many of the technical terms and algorithms discussed
> might be difficult to follow.

> [!TIP]
> However this book empasises learning in another way: [NOTE](./NOTE.md).
> Projects related to the following information can be found at [PROJECT](./PROJECTS.md).

*State-based Dynamic Programming (State DP)* is a fundamental technique in AI decision-making,
particularly useful for *Markov Decision Processes (MDPs)*. It defines a "state" that captures
all relevant system information and uses dynamic programming to compute optimal strategies.

Consider an AI agent navigating a grid world with obstacles. The goal is to find the minimum path
cost from any start to a goal. The state is the agent's position `(x, y)`. Movements
(`Up`/`Down`/`Left`/`Right`) have a default cost of 1, but obstacles increase the cost.


#### Bellman Equation[^bell]

[^bell]: https://en.wikipedia.org/wiki/Bellman_equation.

The optimal value function `V(x, y)` (minimum cost from `(x, y)`) is computed recursively:

```math
V(x, y) = \min_{a \in \text{Actions}} \left[ \text{Cost}(x, y, a) + V(x', y') \right]
```
- *Cost(x, y, a)*: Immediate cost of action `a` from `(x, y)`.
- *(x', y')*: Next state after action `a`.
- *Goal State*: `V(x_g, y_g) = 0`.


### Bottom-Up DP Approach

Using breadth-first propagation from the goal:

```python
from collections import deque

def min_cost_grid(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    dp = [[float('inf')] * cols for _ in range(rows)]
    directions = [(-1,0), (1,0), (0,-1), (0,1)]  # Up, Down, Left, Right
    
    q = deque([goal])
    dp[goal[0]][goal[1]] = 0  # goal cost is 0

    while q:
        x, y = q.popleft()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # check bounds and obstacles (marked as -1 in grid)
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != -1:
                new_cost = dp[x][y] + 1  # assume movement cost is 1
                if new_cost < dp[nx][ny]:
                    dp[nx][ny] = new_cost
                    q.append((nx, ny))

    return dp[start[0]][start[1]] if dp[start[0]][start[1]] != float('inf') else -1


grid = [
    [0,  0,  0,  0, 0],
    [0, -1, -1,  0, 0],  # -1 = obstacle
    [0,  0,  0, -1, 0],
    [0, -1,  0,  0, 0],
    [0,  0,  0,  0, 0]
]
start = (0, 0)
goal = (4, 4)
print("Minimum cost:", min_cost_grid(grid, start, goal))  # Output: 8
```

Explanation:
1. *DP Table Init*: Tracks minimum cost to reach the goal from each cell.
2. *Breadth-First Propagation*: Updates costs from the goal outward, ensuring optimality.
3. *Obstacle Handling*: Cells with `-1` are blocked.


## Q-Learning for Grid Navigation

*Q-Learning* is a model-free RL algorithm where the agent learns through trial and error.

### Key Differences from State DP
| Feature               | State DP                          | Q-Learning                       |
|-----------------------|-----------------------------------|----------------------------------|
| *Model Requirement* | Full environment model            | Learns from interactions        |
| *Updates*           | Bellman equation (deterministic) | Experience-driven (stochastic)  |
| *Exploration*       | None                              | ε-greedy strategy               |
| *Adaptability*      | Static environment                | Dynamic environments            |


### Q-Learning Implementation

```python
import numpy as np
import random

GRID_SIZE = (5, 5)
ACTIONS = [(0,1), (1,0), (0,-1), (-1,0)]  # Right, Down, Left, Up
GOAL = (4, 4)
OBSTACLES = {(2,2), (3,3)}
LEARNING_RATE = 0.1
DISCOUNT = 0.9
EPSILON = 0.2
EPISODES = 1000
MAX_STEPS = 50  # prevent infinite loops

# init Q-table: (x, y) -> action values
Q = np.zeros((GRID_SIZE[0], GRID_SIZE[1], len(ACTIONS)))

def get_next_state(state, action):
    nx, ny = state[0] + action[0], state[1] + action[1]
    # check boundaries and obstacles
    if (0 <= nx < GRID_SIZE[0] and 0 <= ny < GRID_SIZE[1] and (nx, ny) not in OBSTACLES):
        return (nx, ny)
    return state  # stay if invalid

# training loop
for _ in range(EPISODES):
    state = (0, 0)
    steps = 0
    while state != GOAL and steps < MAX_STEPS:
        steps += 1
        # ε-greedy action
        if random.random() < EPSILON:
            action_idx = random.randint(0, len(ACTIONS)-1)
        else:
            action_idx = np.argmax(Q[state[0], state[1]])

        # perform action
        action = ACTIONS[action_idx]
        next_state = get_next_state(state, action)
        
        # reward
        if next_state == GOAL:
            reward = 10
        elif next_state in OBSTACLES:
            reward = -10  # penalize obstacle attempts
        else:
            reward = -1  # default movement cost

        # Q-value update
        old_value = Q[state[0], state[1], action_idx]
        next_max = np.max(Q[next_state[0], next_state[1]])
        new_value = (1 - LEARNING_RATE) * old_value + LEARNING_RATE * (reward + DISCOUNT * next_max)
        Q[state[0], state[1], action_idx] = new_value

        state = next_state

# extract optimal policy
policy = []
for i in range(GRID_SIZE[0]):
    row = []
    for j in range(GRID_SIZE[1]):
        if (i,j) == GOAL:
            row.append('G')
        elif (i,j) in OBSTACLES:
            row.append('X')
        else:
            action = np.argmax(Q[i,j])
            row.append(['→','↓','←','↑'][action])
    policy.append(row)

for r in policy:
    print(' '.join(r))
```

Adjustments:
1. *Obstacle Handling*: Correctly block movement into obstacles.
2. *Step Limit*: Prevents infinite episodes.
3. *Reward Structure*: Penalises invalid moves.


### Deep Q-Network (DQN)

This code (see '[dqn.py](dqn.py)') is about teaching a computer program to make
smart decisions on its own. Imagine a simple game where the player starts at one
end of a board and needs to reach a goal at the other end. The player can move
*left* or *right* at each step. 

At first, the program doesn't know which moves are good - it just tries random
actions. But over time, it learns which actions lead to success by receiving rewards
(negative points for each step, big positive points for reaching the goal). The
program gradually learns to prefer actions that lead to higher rewards.

This type of learning is called "reinforcement learning," and the specific method
used here is Deep Q-Learning, which uses a small neural network to help the program
remember what it has learned.


### Detailed Explanation of the Code

The code implements a Deep Q-Network (DQN), which is a reinforcement learning
algorithm that combines Q-learning with deep neural networks.

Neural Network (DQN Class):
- One input layer (size equal to the state representation)
- One hidden layer with tanh activation
- One output layer (size equal to the number of possible actions)

The neural network takes the current state as input and outputs estimated
"Q-values" for each possible action. These Q-values represent the expected
future reward for taking each action.

Environment (SimpleEnvironment Class):
- 3 states (0=start, 1=middle, 2=goal)
- 2 possible actions (0=left, 1=right)
- Rewards: -1 for each step, +10 for reaching the goal

The environment handles:
- Resetting to the initial state
- Processing actions and returning the next state
- Calculating rewards
- Determining when the episode is complete (reaching the goal)


### Experience Replay (ReplayBuffer Class)

This stores past experiences as tuples of (state, action, reward, next_state, done).
The agent learns by randomly sampling from this buffer, which helps break the correlation
between consecutive experiences and makes learning more stable.

Agent (DQNAgent Class):
- Decides actions using an epsilon-greedy strategy (sometimes random, sometimes best known)
- Stores experiences in the replay buffer
- Learns by updating the Q-network's weights
- Maintains two networks (main and target) to stabilise learning

The training process:
1. Agent observes the current state
2. Agent selects an action (exploring randomly or exploiting learned knowledge)
3. Environment processes the action and returns a new state and reward
4. Experience is stored in the replay buffer
5. Agent samples past experiences and updates its neural network
6. Process repeats until the agent learns an optimal policy

The DQN algorithm has been hugely influential in reinforcement learning and was used in
breakthrough applications like teaching computers to play Atari games and more complex
games like Go and StarCraft at superhuman levels.



1. *Bellman Equation*: The core update formula used in the learning process is directly
derived from the Bellman optimality equation (see above):
```python
target_q_values[i, actions[i]] = rewards[i] + (1 - dones[i]) * self.gamma * max_next_q[i]
```

This is essentially implementing `Q(s,a) = R(s,a) + γ · max_a' Q(s',a')`, which is the
classic dynamic programming update rule for optimal value functions.

2. *Value Iteration*: The iterative process of updating Q-values is a form of value iteration,
another classic dynamic programming algorithm. Instead of using a table to store values,
DQN uses a neural network as a function approximator.

3. *State-Value Relationship*: The algorithm maintains estimates of the value of each
state-action pair and uses these estimates to make decisions, which is central to
dynamic programming.

4. *Bootstrapping*: The learning process uses current estimates of future values to
update current value estimates - this "bootstrapping" approach is a hallmark of
dynamic programming.


### Summary

While DQN has dynamic programming at its core, it differs in several important ways:

- *Function Approximation*: Traditional dynamic programming uses tables to store values
  for each state-action pair. DQN uses a neural network to approximate these values, 
  allowing it to handle larger state spaces.

- *Sample-Based Updates*: Pure dynamic programming updates all state-action values in
  each iteration (full backups). DQN only updates based on sampled experiences
  (partial backups).

- *Model-Free Approach*: Traditional dynamic programming requires a complete model of
  the environment (transition probabilities and rewards). DQN learns directly from
  experience without needing a model.

- *Experience Replay*: The use of stored experiences for learning isn't part of
  traditional dynamic programming.

In essence, DQN takes the mathematical foundation of dynamic programming (the Bellman equation)
and adapts it to work with neural networks and sampling-based learning, allowing it to scale to
problems where traditional dynamic programming would be impractical due to the curse of
dimensionality.[^curse]

[^curse]: https://en.wikipedia.org/wiki/Curse_of_dimensionality

The simple environment in this code is small enough that traditional dynamic programming would
actually work just fine--a simple 3×2 Q-table could solve this problem without needing a neural
network. The DQN approach is really overkill for this problem but demonstrates principles that
scale to much more complex environments.
