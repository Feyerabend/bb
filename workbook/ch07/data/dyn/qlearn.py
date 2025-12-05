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

# testing learned policy
def test_policy():
    state = (0, 0)
    steps = 0
    while state != GOAL and steps < MAX_STEPS:
        steps += 1
        action_idx = np.argmax(Q[state[0], state[1]])
        action = ACTIONS[action_idx]
        next_state = get_next_state(state, action)
        print(f"Step {steps}: Move {['→','↓','←','↑'][action_idx]} to {next_state}")
        state = next_state
        if state == GOAL:
            print("Reached the goal!")
            break
    if state != GOAL:
        print("Failed to reach the goal within max steps.")
test_policy()
# The policy is printed as a grid where:
# - 'G' indicates the goal
# - 'X' indicates an obstacle
# - '→', '↓', '←', '↑' indicate the best action to take from that cell
# The test_policy function demonstrates how the learned policy performs in the environment.
# The Q-learning algorithm is implemented to learn the optimal policy for navigating a grid with obstacles.
