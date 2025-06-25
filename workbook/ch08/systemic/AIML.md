
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



