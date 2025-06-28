
## Non-Monotonic Reasoning

In 1988 I bought: Ginsberg, M. L. (Ed.). (1987). *Readings in nonmonotonic reasoning*.
Morgan Kaufmann.

*Non-monotonic reasoning* (NMR) was a major topic of interest in artificial intelligence
(AI) in the 1980s. Monotonic reasoning is what classical logic does: adding new premises
never reduces the set of conclusions. In contrast, non-monotonic reasoning allows that
adding new knowledge can invalidate previous conclusions.

Example:
- Premise: "Birds can fly" --> conclude Tweety can fly.
- New information: "Tweety is a penguin" --> retract previous conclusion.

This models human-like reasoning better than classical logic, especially in the presence
of defaults, exceptions, and incomplete knowledge. However it deviates from classical
logic in a way that might rub your skin in the wrong way.

In the late '80s, NMR seemed like a promising direction for AI. At the same time,
*Situation Theory/Semantics* began to gain attention (Jon Barwise & John Perry,
*Situations and Attitudes*, 1983). It emphasised understanding human action and
intention within specific social and practical contexts, rather than relying on abstract
logical formalisms alone. It proposed that reasoning is embedded in situations--structured
by goals, roles, and constraints--and cannot be reduced to rules or formal inference.
As I still was occationally connected to the Philosophical Institution, we had some
discussions and seminars on this, for us, fresh topic.

This shift also challenged the AI community to think beyond symbolic manipulation.
It suggested that intelligence isn't just about rules or facts, but also about navigating
changing situations, often with incomplete or conflicting information. It was a turn
toward contextual, dynamic reasoning--something NMR had opened the door to, but situational
approaches made explicit.

Both lines of thought pushed AI toward more flexible, realistic models of reasoning.


### Why Was It Hot in the 1980s?

Thus in the late '70s and '80s, AI researchers realised that classical logic could not capture
how humans deal with uncertainty, defaults, and change. This led to a surge of interest in:
- Default logic (Reiter, 1980)
- Circumscription (McCarthy)
- Autoepistemic logic (Moore)
- Truth maintenance systems (TMS) (Doyle)
- Non-monotonic modal logics

These formalisms aimed to provide a rigorous foundation for reasoning systems that could:
- Make assumptions by default
- Retract assumptions when contradictory information arises
- Update beliefs in light of new evidence

What happened after the 1980s is not that non-monotonic reasoning disappeared, but that
it evolved and fragmented into several interconnected research directions. Its formal
tools--like the above default logic, circumscription, and autoepistemic logic--were
foundational but often proved difficult to scale or implement efficiently. Instead, more
practical and computationally grounded frameworks emerged, particularly in logic programming
and belief revision. One such outcome is *Answer Set Programming* (ASP), which took shape
in the 1990s and matured into a powerful declarative programming paradigm. ASP retains
the core ideas of non-monotonic reasoning and is widely used today in areas like planning,
diagnosis, and combinatorial search. Meanwhile, the ideas of defeasibility and belief
updating spread into fields like knowledge representation, agent systems, and legal reasoning.
Even now, as AI trends shift toward neural methods, non-monotonic reasoning continues to
inform explainability research and hybrid symbolic–neural models, making its legacy a
persistent undercurrent in the broader AI landscape.


### Connections to Other Concepts

a. Logic Programming
- Negation as failure in Prolog is a form of non-monotonic reasoning.
- Led to Answer Set Programming (ASP)--development rooted in stable
  model semantics (Gelfond & Lifschitz).

b. Belief Revision
- The AGM theory (Alchourrón, Gärdenfors, Makinson) formalised how
  agents should revise beliefs.[^agm]
- Closely related to NMR in managing belief updates.

[^agm]: The central insight behind AGM theory is that real-world reasoning isn't static: agents often need to give up beliefs, modify them, or incorporate new ones in light of changing evidence. Traditional logical systems, particularly classical logic, assume that once a belief is held (i.e. derived from axioms), it remains unless a contradiction is encountered. But in practical reasoning, especially under uncertainty or incomplete knowledge, beliefs often have to be revised even in the absence of contradictions. AGM provides a formal structure for doing this in a coherent way.

c. Reasoning about Actions
- Frame problem and qualifications in AI planning required default
  and non-monotonic reasoning.
- Influenced the development of action formalisms (e.g., situation
  calculus, event calculus).

d. Modal and Epistemic Logics
- Autoepistemic logic formalised an agent's introspection (what it
  knows about what it knows), inherently non-monotonic.


### What Happened After the 1980s?

The NMR field did not disappear, but it transformed and was absorbed
into other areas:

a. Answer Set Programming (ASP)
- ASP emerged in the 1990s from the stable model semantics of
  logic programs.
- Today it's used for combinatorial problems, planning,
  bioinformatics, and knowledge representation.

b. Knowledge Representation and Reasoning (KR&R)
- NMR is a core topic in KR.
- Description logics (for ontologies) mostly use monotonic reasoning,
  but extensions have been proposed for non-monotonic variants.

c. Computational Complexity
- Foundational work in the '80s and '90s showed many NMR formalisms
  are computationally hard (often Σ₂^P-complete or worse).
- This pushed focus toward tractable fragments and practical implementations.

d. AI Subfields That Incorporated NMR Ideas
- Commonsense reasoning
- Qualitative reasoning
- Legal reasoning
- Cognitive architectures (e.g. SOAR, ACT-R use TMS ideas)


### Is Non-Monotonic Reasoning Still Relevant Today?

Sure, in at least three directions:

a. Logic-Based AI
- ASP is actively used in AI research and competitions.
- Planning, diagnosis, and verification tasks benefit
  from NMR-style reasoning (Non-Monotonic Reasoning).

b. Explainable AI (XAI)
- NMR contributes to explainability via explicit reasoning
  paths, contrastive reasoning, and counterfactuals.

c. Combining Symbolic and Subsymbolic AI
- Hybrid models try to blend deep learning with logic-based
  reasoning.
- NMR principles help in dealing with uncertain or defeasible
  symbolic knowledge.

d. Knowledge Graphs & Ontologies
- Researchers explore default reasoning over graphs, semantic
  web rules, and non-monotonic extensions to OWL.


### Modern Examples and Projects

- DLV system (ASP solver)
- Clingo (modern ASP system combining logic programming with control)
- Commonsense KBs like Cyc and ConceptNet, where defaults and defeasibility are key
- AI planning tools like PDDL+, handling default effects


### Suggested Literature for Follow-Up

Brachman, R. J., & Levesque, H. J. (2022). *Knowledge representation and reasoning* (2nd ed.). MIT Press.

Brewka, G. (1991). *Nonmonotonic reasoning: Logical foundations of commonsense* (Vol. 12). Cambridge University Press.

Gebser, M., Kaminski, R., Kaufmann, B., & Schaub, T. (2012). Answer set solving in practice. Morgan & Claypool Publishers.

For hands-on practice look into tools like:
- clingo: https://potassco.org/clingo/
- DLV: http://www.dlvsystem.com/


### Summary

Non-monotonic reasoning introduced the idea that conclusions can be retracted in the
light of new evidence--crucial for human-like reasoning. While its initial wave was
theoretical and peaked in the 1980s, its principles evolved into more practical systems
(like ASP) and remain relevant in today's logic-based AI and explainable reasoning
efforts.

