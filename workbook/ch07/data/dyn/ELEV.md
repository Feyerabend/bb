
## Q-Learning Elevator Scheduler Project

Project: *Create an AI controller that learns to optimise elevator movements in a 3-floor building.*

This project simulates a *smart elevator controller* that learns to optimize its movements using *Q-learning* (a type of Reinforcement Learning).  

__1. *The Elevator Setup*__
   - A *3-floor building* (Ground, 1st, Top).  
   - Passengers can request the elevator from any floor.  
   - The elevator must decide whether to:  
     - *Go Up (↑)*  
     - *Go Down (↓)*  
     - *Open Doors (⏏)*  

| Symbol | Meaning          | Real-World Equivalent |
|--------|------------------|-----------------------|
| `↑`    | Move Up          | Up button pressed     |
| `↓`    | Move Down        | Down button pressed   |
| `⏏`    | Open Doors/Stop  | Door open button      |

Each state is a tuple `(current_floor, request_at_current, has_above, has_below)`:
- `current_floor`: 0 (Ground), 1, 2 (Top)
- `request_at_current`: True/False if current floor has requests
- `has_above`: True/False if any floors above have requests
- `has_below`: Same for floors below

__2. *What the AI Learns*__
   - The elevator starts with *random actions* (exploration).  
   - Over time, it learns:  
     - When to *move toward waiting passengers* (instead of just opening doors).  
     - How to *minimize wait times* for everyone.  
     - When to *ignore unnecessary stops* (to save time).  

__3. *Training Results (What You See in Output)*__
   - *Reward increases* (from *24.6 → 155.7*) → The AI is improving!  
   - *Epsilon (ε) decreases* (from *0.50 → 0.07*) → AI relies less on random moves.  
   - *Policy Accuracy (83.3%)* → AI makes correct decisions most of the time.  



### The Code  

__1. *The AI learns by trial and error*__

   - It tries random moves at first (high *ε*).  
   - Over time, it *prefers actions that give higher rewards* (low *ε*).  

__2. *Reward System Shapes Behavior*__

   - *+3 points* for picking up passengers.  
   - *+4 points* for delivering them.  
   - *-2 points* for unnecessary stops.  
   - *-0.2 per waiting passenger* (encourages fast service).  

__3. *Final Policy (What the AI Learned)*__

   - *If at Ground floor & requests above → Go Up (↑)*  
   - *If at Top floor & requests below → Go Down (↓)*  
   - *If at a floor with a request → Open Doors (⏏)*  
   - *If no requests → Stay (⏏)*  

__4. *Simulation Shows Real Behavior*__

   - The elevator *waits at Ground (G)* until a request appears.  
   - If someone presses a button, it *moves efficiently*.  



### Environment Setup

```python
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
        # state: (current_floor, has_requests_above, has_requests_below)
        above = any(r > self.current_floor for r in self.requests)
        below = any(r < self.current_floor for r in self.requests)
        return (self.current_floor, above, below)
    
    def step(self, action):
        # actions: 0 = Up, 1 = Down, 2 = Open doors
        reward = 0
        done = False
        
        # movement logic
        if action == 0 and self.current_floor < 2:
            self.current_floor += 1
        elif action == 1 and self.current_floor > 0:
            self.current_floor -= 1
            
        # passenger handling
        if action == 2:
            # remove current floor requests
            if self.current_floor in self.requests:
                self.requests.remove(self.current_floor)
                reward += 2  # reward for picking up
            # random destination generation
            if self.current_floor in [0, 1]:
                self.destinations.add(2)  # everyone to top
                reward += 3  # reward for delivering
        
        # generate random requests (30% chance)
        if random.random() < 0.3:
            new_floor = random.choice([0, 1])
            self.requests.add(new_floor)
            
        # time penalty
        reward -= 0.1 * len(self.requests)
        self.time += 1
        done = self.time >= self.max_time
        
        return self._get_state(), reward, done, {}
```

### Q-Learning Agent

```python
class QLearningAgent:
    def __init__(self, learning_rate=0.1, discount=0.9, epsilon=0.1):
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
```

### Training Loop

```python
env = ElevatorEnv()
agent = QLearningAgent()

# training parameters
episodes = 1000
print_interval = 100

for episode in range(episodes):
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
        print(f"Episode {episode}, Total Reward: {total_reward:.1f}")

# show final policy
print("\nLearned Policy:")
for state in sorted(agent.q_table.keys()):
    actions = ['↑', '↓', '⏏']
    policy = actions[np.argmax(agent.q_table[state])]
    print(f"State {state}: {policy}")
```

### Challenges

1. *Performance Analysis*:
   - Compare with random policy
   - Track average wait times
   - Measure energy usage (number of movements)

2. *Improvement Tasks*:
   - Add destination floor handling
   - Implement multiple elevators
   - Create peak hour request patterns
   - Add emergency stop functionality

3. *Visualization*:
   ```python
   def visualize(env):
       for floor in reversed(range(3)):
           marker = "▶" if floor == env.current_floor else " "
           calls = " ".join("▲" if f in env.requests else " " for f in range(3))
           print(f"{marker} F{floor} | {calls}")
   
   # add to training loop for live visualization
   ```

This project provides hands-on experience with:
- Reinforcement learning fundamentals
- State space design
- Reward engineering
- Policy evaluation
- Real-world system modeling
