
## Projects for Dynamic Programming

Before reading and starting your project,
please read the [NOTE](./NOTE.md).


__1. Maze Modifier Challenge__

Modify the State DP grid code to handle:
- Different movement costs (e.g., "mud tiles" with cost 3)
- Diagonal movements
- Teleportation portals between cells

Outcomes
- Understanding state transitions
- Experimenting with cost functions
- Basic algorithm modification skills


__2. Q-Learning Explorer__

Implement the Q-Learning grid world and:
- Create a visualization of the policy at different training stages
- Track how often the agent reaches the goal during training
- Experiment with different ε values (0.1 vs 0.5)

Deliverables
- Animated policy evolution
- Graph of success rate vs episodes


__3. Algorithm Showdown__

Compare State DP and Q-Learning
- Use identical grid worlds
- Measure computation time
- Compare resulting path costs
- Create a report on when each method is preferable

Example Grid
```python
grid = [
    [0,  0,  0, 0],
    [0, -1, -1, 0],
    [0,  0,  0, 0]
]
```


__4. Pac-Man Pathfinder__

Create a simplified Pac-Man game where:
- Pac-Man uses State DP to find ghosts
- Ghosts move randomly
- Students implement the reward system
- Bonus: Add power pellets that change movement costs

Required: Python + PyGame (basic)


__5. Dynamic Maze Solver__

Extend the Q-Learning code to handle:
- Moving obstacles
- Changing goal positions
- Periodic maze resets

*Can the agent adapt to changes faster than complete retraining?*


__6. DQN Diagnostics__

Analyze the simple DQN code by:
- Plotting loss curves during training
- Visualizing the neural network's decision boundaries
- Experimenting with different network architectures

```python
# try changing the network structure
self.net = nn.Sequential(
    nn.Linear(state_size, 8),
    nn.ReLU(),
    nn.Linear(8, action_size)
)
```


__7. Real-World RL__

Apply Q-Learning to a real-world scenario:
- [Elevator scheduling](./ELEV.md)
- Traffic light control
- Robot vacuum pathing

Requirements
- Define states/actions/rewards
- Implement a simplified simulation
- Train and evaluate policy effectiveness


__8. Curriculum Learning Challenge__

Implement a tiered learning system:
1. Train on 3x3 grids first
2. Progressively increase grid size
3. Compare with direct 5x5 training

Track
- Time to convergence
- Final policy quality
- Sample efficiency
