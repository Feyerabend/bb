import numpy as np
import random

class ElevatorEnv:
    def __init__(self):
        self.floors = 3
        self.current_floor = 0  # ground floor
        self.requests = set()    # pending floor requests
        self.destinations = set()
        self.time = 0
        self.max_time = 50
        
    def reset(self):
        self.current_floor = 0
        self.requests = set()
        self.destinations = set()
        self.time = 0
        return self._get_state()

    def _get_state(self):
        #  state representation
        current = self.current_floor in self.requests
        above = any(r > self.current_floor for r in self.requests)
        below = any(r < self.current_floor for r in self.requests)
        return (self.current_floor, current, above, below)

    def step(self, action):
        # actions: 0 = Up, 1 = Down, 2 = Open doors
        reward = 0
        done = False
        
        #  current state features
        _, current_req, has_above, has_below = self._get_state()
        
        # movement logic with rewards
        if action == 0 and self.current_floor < 2:
            self.current_floor += 1
            if has_above:
                reward += 0.5  # reward productive movement
        elif action == 1 and self.current_floor > 0:
            self.current_floor -= 1
            if has_below:
                reward += 0.5  # reward productive movement
            
        # passenger handling with improved rewards
        if action == 2:
            if self.current_floor in self.requests:
                self.requests.remove(self.current_floor)
                reward += 3  # increased reward for picking up
            else:
                reward -= 2  # increased penalty for unnecessary stops
                
            # destination handling
            if self.current_floor in [0, 1]:
                self.destinations.add(2)
                reward += 4  # increased reward for delivering
        
        # generate random requests (30% chance)
        if random.random() < 0.3:
            new_floor = random.choice([0, 1])
            self.requests.add(new_floor)
            
        # time penalty based on waiting requests
        reward -= 0.2 * len(self.requests)  # increased penalty
        self.time += 1
        done = self.time >= self.max_time
        
        return self._get_state(), reward, done, {}

    def render(self):
        floor_names = ["G", "1", "2"]
        print(f"\nTime {self.time}: [ {floor_names[self.current_floor]} ]")
        print("Requests:", self.requests)
        print("Destinations:", self.destinations)


class QLearningAgent:
    def __init__(self, learning_rate=0.1, discount=0.95, epsilon=0.5):  # adjusted parameters
        self.q_table = {}
        self.lr = learning_rate
        self.discount = discount
        self.epsilon = epsilon
        
    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.choice([0, 1, 2])
        
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]
            
        return np.argmax(self.q_table[state])
    
    def update(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]
        if next_state not in self.q_table:
            self.q_table[next_state] = [0, 0, 0]
            
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        
        new_value = (1 - self.lr) * old_value + self.lr * (reward + self.discount * next_max)
        self.q_table[state][action] = new_value


def explain_policy(state, action):
    floor_names = ["Ground", "1st", "Top"]
    arrows = {0: "↑(Up)", 1: "↓(Down)", 2: "⏏(Open)"}
    print(f"At {floor_names[state[0]]} floor: "
          f"Current{'✔' if state[1] else '✖'}, "
          f"Above{'✔' if state[2] else '✖'}, "
          f"Below{'✔' if state[3] else '✖'} → "
          f"Action: {arrows[action]}")


def test_policy(agent):
    test_cases = [
        ((0, False, True, False), 0),   # Should go up when requests above
        ((0, True, True, False), 0),    # Should prioritize moving up
        ((2, False, False, True), 1),   # Should go down when requests below
        ((1, True, False, False), 2),   # Should open when current floor has request
        ((1, False, True, True), 0),    # Should prioritize up when both directions
        ((0, False, False, False), 2)   # Should wait when no requests
    ]
    
    correct = 0
    for state, expected in test_cases:
        if state not in agent.q_table:
            agent.q_table[state] = [0, 0, 0]
        action = np.argmax(agent.q_table[state])
        explain_policy(state, action)
        correct += (action == expected)
    
    print(f"\nPolicy Accuracy: {correct/len(test_cases)*100:.1f}%")



env = ElevatorEnv()
agent = QLearningAgent(epsilon=0.5)  # initial exploration

episodes = 2000
print_interval = 200

for episode in range(episodes):
    if episode > 0 and episode % 200 == 0:
        agent.epsilon = max(0.05, agent.epsilon * 0.8)  # more gradual decay
    
    state = env.reset()
    total_reward = 0
    
    while True:
        action = agent.get_action(state)
        next_state, reward, done, _ = env.step(action)
        agent.update(state, action, reward, next_state)
        total_reward += reward
        state = next_state
        if done:
            break
    
    if episode % print_interval == 0:
        print(f"Episode {episode}, ε={agent.epsilon:.2f}, Total Reward: {total_reward:.1f}")

# evaluation
print("\n Final Evaluation of Policy:")
test_policy(agent)

print("\nLearned Policy:")
for state in sorted(agent.q_table.keys()):
    actions = ['↑', '↓', '⏏']
    policy = actions[np.argmax(agent.q_table[state])]
    print(f"State {state}: {policy}")

print("\n Sample Simulation of Elevator:")
state = env.reset()
env.render()
for _ in range(10):
    action = agent.get_action(state)
    state, _, done, _ = env.step(action)
    env.render()
    if done:
        break

print("Simulation finished.")
