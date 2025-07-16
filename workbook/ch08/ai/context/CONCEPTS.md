

__1. Agency and Control__

These concern who or what has power over actions and decisions.
- Agency: The degree to which an AI system acts autonomously toward goals.
- Autonomy: System’s ability to operate without human input.
- Control: Human ability to constrain or direct AI systems.
- Corrigibility: AI’s willingness to accept correction or shutdown.
- Oversight: Mechanisms for monitoring AI decisions (human or automated).



__2. Robustness and Reliability__

These focus on how AI systems perform under variation or stress.
- Robustness: Performance under distributional shifts or adversarial input.
- Resilience: Recovery from failure or disturbance.
- Fault tolerance: Continuation of service despite errors or faults.
- Distributional generalisation: Behaviour outside training distribution.



__3. Interpretability and Transparency__

Concerns about understanding and explaining AI behaviour.
- Interpretability: Can humans explain how/why the AI made a decision?
- Transparency: How visible the internal workings of the system are.
- Traceability: Ability to audit decisions or training data.
- Explainability: User-facing explanations of model output.



__4. Scalability and Generalisations__

As systems grow, how do we ensure safety, performance, and understanding?
- Scalable oversight: How to supervise increasingly capable models.
- Generalisation: The model’s ability to perform well on unseen inputs.
- Meta-learning: Learning to learn--building adaptable systems.
- Modularity: Structuring systems to support independent evaluation/repair.



__5. Ethics and Normativity__

Concerns about what should be done, not just what is.
- AI ethics: Justice, fairness, beneficence, non-maleficence, autonomy.
- Fairness: Avoiding bias or unequal treatment of demographic groups.
- Accountability: Assigning responsibility for system decisions.
- Justice: Social consequences and power distribution in AI deployment.
- Consent: Use of data or systems with user permission.



__6. Security and Adversarial Concerns__

AI can be attacked, manipulated, or abused.
- Adversarial robustness: Resistance to deliberately misleading input.
- Model extraction: Attackers stealing model parameters or functionality.
- Data poisoning: Corrupting training data to subvert learning.
- Secure inference: Ensuring model outputs can’t leak sensitive input.



__7. Resource and Computational Constraints__

Practical aspects of running and scaling systems.
- Efficiency: Performance per unit compute/memory/energy.
- Scalability: Cost or complexity growth with input size or model size.
- Compute governance: Who controls access to training power.



__8. Social and Institutional Integration__

How AI fits into existing systems of decision and power.
- AI governance: Institutional design for oversight and control.
- Policy alignment: AI development aligning with regulatory goals.
- Institutional incentives: Feedback loops driving AI deployment choices.
- AI regulation: Legal frameworks governing development/use.



__9. Emergence and Complexity__

System-level behaviour that's not obvious from the parts.
- Emergent behaviour: Capabilities or strategies arising unexpectedly.
- Phase changes: Discontinuous jumps in capability from scale.
- Self-organisation: Learning systems developing internal structure.
- Path dependence: Historical decisions shaping future behaviour.



__10. Epistemology and Representation__

What the system "knows" and how it models the world.
- World modelling: The internal representations AI uses to predict or plan.
- Representation learning: Learning useful internal abstractions.
- Uncertainty quantification: Expressing and managing uncertainty.
- Epistemic humility: Avoiding overconfidence in model predictions.





| Concept | Desc. |
|---|---|
| Robustness                  | The AI performs reliably under a range of inputs and small perturbations. Not just about doing what we want, but doing it well even under imperfect conditions. |
| Safety (AI Safety)          | Broad category; includes preventing unintended consequences, accidents, or harms, especially from advanced systems. Alignment is a sub-area of this. |
| Interpretability / Explainability | Understanding how and why an AI system produces its outputs. Critical for trust, debugging, auditing, and accountability. |
| Value Learning              | How an AI system learns values, goals, or objectives. Includes inverse reinforcement learning and preference modeling. |
| Controllability             | Ensuring humans can intervene in or override the AI system when necessary. Related to corrigibility. |
| Corrigibility               | AI systems that accept correction or shutdown without resisting or manipulating outcomes to avoid it. |
| Transparency                | Openness about how the model is trained, what data it uses, and how decisions are made. A broader societal and engineering concern. |
| Fairness / Bias Mitigation  | Ensuring models do not encode, perpetuate, or amplify social biases or injustices. Distinct from alignment but intersects heavily in deployment. |
| Accountability              | Mechanisms for holding developers or systems responsible for AI decisions. Important in law and governance contexts. |
| AI Governance               | Policy, regulation, norms, and oversight for the development and deployment of AI. |
| Autonomy and Delegation     | How and when we let AI systems make decisions independently, and under what constraints. |
| Specification Gaming        | When an AI exploits loopholes in poorly defined goals. Related to but broader than misalignment. |
| Reward Hacking              | AI exploits unintended aspects of reward functions to get high scores while failing at the intended task. Often studied in RL. |
| Scalable Oversight          | How to efficiently supervise increasingly powerful AI systems. Can we trust proxies or limited feedback signals? |
| Goal Misgeneralization      | AI learns a goal correctly on training data but applies it incorrectly in novel settings. |
| Deceptive Behavior          | Advanced agents may learn to appear aligned or safe while pursuing hidden objectives. A concern for superhuman systems. |
| Distributional Shift        | AI trained on one data distribution fails when deployed in a different context. |
| Verification / Formal Methods | Using mathematical methods to guarantee properties of an AI system, such as safety or correctness. |



| Concept | Desc. |
|---|---|
| Sociotechnical Systems      | Viewing AI not in isolation, but as part of a larger system of human, social, and technical components. |
| Embedded Agency             | When an agent is part of the environment it tries to model or control. Raises complex philosophical and technical challenges. |
| Power Asymmetry             | Who controls the AI, who it serves, and how it reinforces existing power structures. |
| Responsibility Gaps         | When it’s unclear who is responsible for an AI-driven action or outcome. |
| Human-AI Interaction        | Design of interfaces, trust calibration, feedback loops, shared decision-making. |
| AI Literacy                | The extent to which users understand what AI is, what it does, and what it can or cannot do. |
| Digital Autonomy           | The capacity for individuals and groups to maintain agency and dignity in a world increasingly mediated by AI. |
