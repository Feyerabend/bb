import numpy as np
from collections import deque
import random

class DQN:
    def __init__(self, input_size, hidden_size, output_size, lr=0.01):
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
        self.lr = lr

    def forward(self, X):
        # ensure X is properly shaped
        if X.ndim == 1:
            X = X.reshape(1, -1)
            
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        return self.z2
    
    def predict(self, X):
        # forward pass without storing intermediate values
        if X.ndim == 1:
            X = X.reshape(1, -1)
            
        z1 = np.dot(X, self.W1) + self.b1
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        return z2

    def backward(self, X, y_target):
        # make sure X is properly shaped
        if X.ndim == 1:
            X = X.reshape(1, -1)
            
        # forward pass
        output = self.forward(X)
        
        # error calculation (MSE derivative)
        error = output - y_target
        
        # backpropagation
        dW2 = np.dot(self.a1.T, error)
        db2 = np.sum(error, axis=0, keepdims=True)
        
        d_a1 = np.dot(error, self.W2.T)
        d_z1 = d_a1 * (1 - np.square(self.a1))  # derivative of tanh
        
        dW1 = np.dot(X.T, d_z1)
        db1 = np.sum(d_z1, axis=0, keepdims=True)
        
        # update weights with learning rate
        self.W1 -= self.lr * dW1
        self.b1 -= self.lr * db1
        self.W2 -= self.lr * dW2
        self.b2 -= self.lr * db2
        
        return np.mean(np.square(error))  # return loss for monitoring

    def copy_weights_from(self, other_network):
        # copy weights from other network
        self.W1 = other_network.W1.copy()
        self.b1 = other_network.b1.copy()
        self.W2 = other_network.W2.copy()
        self.b2 = other_network.b2.copy()


class SimpleEnvironment:
    def __init__(self):
        self.state = 0  # States: 0 (start), 1 (middle), 2 (goal)
        
    def reset(self):
        self.state = 0
        return self._one_hot(self.state)
    
    def step(self, action):
        # actions: 0 (left), 1 (right)"""
        reward = -1  # default step penalty
        done = False
        
        if action == 1 and self.state < 2:  # move right
            self.state += 1
        elif action == 0 and self.state > 0:  # move left
            self.state -= 1
            
        if self.state == 2:  # reach goal
            reward = 10
            done = True
            
        return self._one_hot(self.state), reward, done, {}
    
    def _one_hot(self, state):
        # convert state to one-hot encoding
        one_hot = np.zeros(3)
        one_hot[state] = 1
        return one_hot


class ReplayBuffer:
    def __init__(self, capacity=1000):
        self.memory = deque(maxlen=capacity)
        
    def add(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
        return random.sample(self.memory, min(len(self.memory), batch_size))
    
    def __len__(self):
        return len(self.memory)


class DQNAgent:
    def __init__(self, state_size=3, hidden_size=16, action_size=2, lr=0.01):
        # main network for training
        self.q_network = DQN(state_size, hidden_size, action_size, lr)
        # target network for stable Q-targets
        self.target_network = DQN(state_size, hidden_size, action_size, lr)
        self.target_network.copy_weights_from(self.q_network)
        
        # hyperparameters
        self.gamma = 0.99  # discount factor
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.target_update_freq = 10  # update target network every N episodes
        
        # experience replay
        self.replay_buffer = ReplayBuffer(capacity=2000)
        self.batch_size = 32
        
    def act(self, state):
        # epsilon-greedy action selection
        if np.random.rand() < self.epsilon:
            return np.random.randint(2)  # random action
        
        q_values = self.q_network.predict(state)
        return np.argmax(q_values)
    
    def store_experience(self, state, action, reward, next_state, done):
        self.replay_buffer.add(state, action, reward, next_state, done)
    
    def learn(self):
        # check if enough samples in replay buffer
        if len(self.replay_buffer) < self.batch_size:
            return 0
        
        # sample batch of experiences
        batch = self.replay_buffer.sample(self.batch_size)
        states = np.vstack([experience[0] for experience in batch])
        actions = np.array([experience[1] for experience in batch])
        rewards = np.array([experience[2] for experience in batch])
        next_states = np.vstack([experience[3] for experience in batch])
        dones = np.array([experience[4] for experience in batch], dtype=np.float32)
        
        # current Q-values
        current_q_values = self.q_network.predict(states)
        
        # next Q-values from target network
        next_q_values = self.target_network.predict(next_states)
        max_next_q = np.max(next_q_values, axis=1)
        
        # create target Q-values
        target_q_values = current_q_values.copy()
        for i in range(self.batch_size):
            target_q_values[i, actions[i]] = rewards[i] + (1 - dones[i]) * self.gamma * max_next_q[i]
        
        # update Q-network
        loss = self.q_network.backward(states, target_q_values)
        
        # decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return loss
    
    def update_target_network(self):
        self.target_network.copy_weights_from(self.q_network)


def train(env, agent, episodes=500, max_steps=100):
    rewards_history = []
    
    for ep in range(episodes):
        state = env.reset()
        total_reward = 0
        loss = 0
        
        for step in range(max_steps):
            # select action
            action = agent.act(state)
            
            # take action
            next_state, reward, done, _ = env.step(action)
            
            # store experience
            agent.store_experience(state, action, reward, next_state, done)
            
            # learn from experiences
            loss += agent.learn()
            
            # update state and rewards
            state = next_state
            total_reward += reward
            
            if done:
                break
                
        # update target network periodically
        if ep % agent.target_update_freq == 0:
            agent.update_target_network()
            
        rewards_history.append(total_reward)
        
        # print progress
        if (ep + 1) % 50 == 0:
            avg_reward = np.mean(rewards_history[-50:])
            print(f"Episode {ep + 1}/{episodes}, Avg Reward: {avg_reward:.2f}, Epsilon: {agent.epsilon:.2f}")
    
    return rewards_history


def test_agent(env, agent, episodes=10):
    print("\nTesting trained agent:")
    for ep in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        steps = 0
        
        print(f"\nEpisode {ep + 1}:")
        print(f"State: {np.argmax(state)}", end="")
        
        while not done:
            action = agent.act(state)  # use greedy policy
            next_state, reward, done, _ = env.step(action)
            
            print(f" -> Action: {'Left' if action == 0 else 'Right'} -> State: {np.argmax(next_state)}", end="")
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                print(f"\nReached goal in {steps} steps. Total reward: {total_reward}")
                break



if __name__ == "__main__":
    # init components
    env = SimpleEnvironment()
    agent = DQNAgent(state_size=3, hidden_size=16, action_size=2, lr=0.01)
    
    # train, test agent
    rewards = train(env, agent, episodes=500)
    test_agent(env, agent)
