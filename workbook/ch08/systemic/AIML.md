
| Concept       | Impact on AI/ML    | Comments                                                                 |
|---------------|--------------------|--------------------------------------------------------------------------|
| Noise         | High               | Can be both a nuisance and a tool (e.g., regularisation, robustness).    |
| Randomness    | High               | Essential for training algorithms, exploration, generalisation.          |
| Optimisation  | High               | Core to ML; learning = optimisation (loss minimisation).                 |
| Abstraction   | High               | Learned abstractions drive model effectiveness (features, latent spaces).|
| Scalability   | High               | Performance often depends on scaling data, models, compute.              |
| Determinism   | High (in absence)  | Non-determinism affects reproducibility and debugging.                   |
| Complexity    | High               | Directly impacts generalisation, overfitting, interpretability.          |
| State         | High               | Learned, often opaque; critical in temporal models, RL.                  |
| Errors        | High               | Integral to learning process (not just a fault as in classic systems).   |


--
| Security        | Medium              | AI-specific threats exist (adversarial inputs), but conceptually related.|
| Interface       | Medium              | AI models expose APIs, but interface design is not ML-unique.            |
| Latency         | Medium              | Important in real-time inference; shared with other domains.             |
| Concurrency     | Medium              | Needed in ML pipelines; conceptually similar to other domains.           |
| Fault tolerance | Medium              | ML introduces some new cases (e.g., gradient staleness), but many shared principles. |
| Time            | Medium              | Relevant in temporal models (e.g., RNNs), but also in real-time systems. |
| Energy use      | Medium              | Training large models is energy-intensive, but not unique to reasoning.  |
| Cost            | Medium              | Financial and computational cost key in ML, but general issue.           |
| Resilience      | Medium              | ML robustness (e.g., to adversarial input) overlaps with traditional resilience. |
--





Noise
Irregular, unpredictable variations in data, measurements, or signals.
- Degrades performance (e.g., noisy labels, sensor data).- Used in training (e.g., data augmentation, denoising autoencoders) to enhance robustness.
- Mitigating harmful noise.- Balancing beneficial noise for generalisation.
Dual role: a challenge to overcome and a tool to improve model resilience.


Randomness
Non-deterministic elements in processes or decision-making.
- Drives algorithms (e.g., stochastic gradient descent, dropout).- Enables exploration in reinforcement learning and diversity in ensembles.
- Ensuring reproducibility.- Controlling randomness for debugging.
Foundational for exploration and learning, requiring careful balance with control.


Optimization
Adjusting parameters to minimise/maximise an objective function.
- Core to learning (e.g., minimising loss via gradient descent).- Used in hyperparameter tuning, architecture search.
- Handling non-convex, high-dimensional problems.- Developing efficient heuristics.
Underpins AI/ML, solving complex problems under constraints and uncertainty.


Abstraction
Hiding low-level details to create simplified representations.
- Models learn abstractions (e.g., latent features in neural nets).- Enables transfer learning and generalisation.
- Ensuring interpretability.- Auditing opaque abstractions.
Key to model power, but central to trust and understanding challenges.


Scalability
Ability to handle increasing data, compute, or model complexity efficiently.
- Enables breakthroughs (e.g., transformers).- Requires distributed computing and efficient algorithms.
- Managing cost, energy, bias, and accessibility.- Maintaining control at scale.
Critical for advancing AI, balancing efficiency with ethical considerations.


Determinism
Consistent behaviour for identical inputs across executions.
- Often sacrificed for randomness in training.- Supported by tools like random seeds, deterministic modes.
- Achieving reproducibility.- Meeting regulatory needs without stifling exploration.
Balances reliability and flexibility, critical for debugging and compliance.


Complexity
Measure of intricacy in systems, models, or behaviour.
- Complex models capture patterns but risk overfitting.- Simpler models aid interpretability via regularisation, compression.
- Avoiding overfitting and opacity.- Balancing capacity and simplicity.
Essential for robust, interpretable models that generalise well.


State
Information retained across time, inputs, or operations.
- Central to sequential models (e.g., RNNs, LSTMs), reinforcement learning.- Transformers externalise state.
- Debugging and visualising state.- Managing resets for stability.
Enables adaptation in dynamic systems, but complicates transparency.


Errors
Deviations from desired behaviour or accuracy.
- Drive learning via loss and feedback.- Can propagate bias or failure if unaddressed.
- Mitigating harmful errors.- Interpreting errors correctly.
Errors are learning signals; their handling impacts model fairness and reliability.

