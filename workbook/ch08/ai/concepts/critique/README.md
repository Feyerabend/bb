
## Critique

Amid intensifying debates over artificial intelligence, where much of the public imagination is gripped
by speculative risks and anthropomorphic projections, a quieter but more grounded tradition of critique
continues to examine AI through the lenses of epistemology, cognitive science, and philosophy of language.
*Melanie Mitchell*, alongside thinkers like *Gary Marcus*, represents a continuation and renewal of this
tradition. Rather than accepting the framing of intelligence as a matter of scale--more data, larger models,
longer training--Mitchell and Marcus both question the conceptual coherence of claims about "understanding"
and "reasoning" in current systems. Their work offers a counterweight to the dominant narratives of progress
by asking more fundamental questions about cognition, representation, and what it actually means to "know."

Mitchell's skepticism about deep learning systems echoes *John Searle's* famous Chinese Room argument,
which proposed that symbol manipulation, no matter how intricate, does not amount to consciousness or
genuine understanding. Like *Donald Davidson*, who emphasised the holistic and interpretive nature of
thought and language, Mitchell is attuned to the context-dependence and world-embeddedness of human
cognition--dimensions that are systematically abstracted away in most contemporary AI. Current models
might generate plausible outputs, but their lack of grounding in the physical and social world means
that they operate without referents, without intentions, and without the capacity to revise beliefs
based on genuine understanding.

*Gary Marcus*, while sharing many of these critiques, brings to the table a long-standing argument from
cognitive science: that *symbolic representation*, *structured knowledge*, and *explicit causal reasoning*
are essential components of intelligent behaviour--components glaringly absent in today's dominant
paradigm. Marcus has consistently pointed out that deep learning systems, though often impressively
fluent, are brittle, opaque, and lack the ability to generalise in the way even young children can.
His critiques often highlight the dangers of overfitting to benchmarks, the absence of mechanisms
for abstraction and transfer, and the failure of purely statistical methods to model reasoning about
the real world. Where Mitchell draws from complexity theory and emergent behaviour, Marcus often brings
the discussion back to *modularity, representation*, and *hybrid architectures* that integrate symbolic
reasoning with statistical learning.

This line of critique situates Mitchell and Marcus among a growing chorus of researchers--including
*Emily Bender*, *Timnit Gebru*, and *Margaret Mitchell*--who warn against mistaking linguistic fluency
for comprehension, and benchmark performance for general intelligence. They argue that these models
do not "know" things in any meaningful sense; they recombine surface patterns learned from training
data without access to the kinds of structured, embodied, and causally coherent world-models that
humans use to reason and act. In this way, Mitchell and Marcus continue a line of thought stretching
back through the philosophy of mind, through early AI critiques, and into the core of what it means
to be an intelligent system.

In the same spirit, Marcus has argued forcefully that *deep learning alone is not enough*--that it
must be complemented by systems capable of abstraction, compositionality, and causal inference. He
has been a vocal advocate for *hybrid models*, which attempt to integrate the strengths of symbolic
reasoning with the pattern-matching capabilities of neural networks. Both he and Mitchell emphasise
not the danger of runaway superintelligence, but the *fragility*, *brittleness*, and *misleading
surface performance* of current systems--problems that become increasingly pressing as these systems
are deployed in high-stakes domains.

Importantly, this tradition of critique diverges sharply from the more speculative narratives of
figures like *Elon Musk*, *Nick Bostrom*, and *Max Tegmark*, whose concerns focus on hypothetical
existential risks posed by omniscient AGI. Mitchell and Marcus instead focus on real, present limitations:
the inability of AI to understand physical causality, social nuance, or moral norms--not in theory,
but in the tangible systems we are building today. Their approach calls for *epistemic humility*,
*cognitive plausibility*, and *methodological pluralism*, emphasising that progress in AI must be
grounded in understanding intelligence as it actually functions, not as we wish it would.

By anchoring their work in empirical science, historical critique, and cognitive realism, Mitchell
and Marcus--like Searle and Davidson before them--offer a far more compelling and constructive
framework for evaluating AI than those fixated on speculative futures. They ask not whether machines
might become gods or monsters, but what it takes to build systems that can reason, adapt, and
interact meaningfully in a complex world--a question that remains, at root, deeply human.

To ground their critiques, Mitchell and Marcus draw on concrete examples that expose the limitations
of current AI systems. For instance, Mitchell's work on analogy-making, exemplified in her *Copycat*
architecture, demonstrates how human-like reasoning requires flexible, context-sensitive
representations that deep learning struggles to replicate. Similarly, Marcus has highlighted
specific failures of large language models, such as GPT's inability to consistently handle
compositional tasks--like understanding novel combinations of familiar concepts--revealing their
reliance on statistical patterns rather than robust generalisation. These examples underscore their
argument that intelligence demands more than scaling up data and compute.

Proponents of deep learning, such as researchers at OpenAI and Google, counter that massive scale
and emergent behaviours can bridge these gaps, citing the impressive performance of models like
GPT-4 and PaLM on diverse benchmarks. They argue that continued scaling, combined with techniques
like fine-tuning and reinforcement learning, may yield systems capable of broader generalisation.
However, Mitchell and Marcus contend that these approaches still fall short of capturing the
structured, causal, and embodied knowledge that humans rely on, as evidenced by AI's persistent
struggles with physical causality and social nuance.

The concept of *cognitive realism*, central to their critiques, refers to designing AI systems that
align with the principles of human cognition--such as modularity, abstraction, and
context-dependence--rather than relying solely on statistical correlations. By emphasising this,
Mitchell and Marcus call for a broader research agenda that integrates insights from cognitive
science and philosophy. Their work also complements the ethical critiques of researchers like
*Emily Bender* and *Timnit Gebru*, who highlight not only cognitive shortcomings but also issues
like algorithmic bias and environmental costs, urging a more holistic evaluation of AI's societal
impact. Together, these perspectives reinforce the need for humility and rigour in AI development,
ensuring that systems are not just performant but meaningfully intelligent in a complex, human world.


### Reference

- Bender, E. M., Gebru, T., McMillan-Major, A., & Mitchell, M. (2021). On the dangers of stochastic
  parrots: Can language models be too big? In *Proceedings of the 2021 ACM Conference on Fairness,
  Accountability, and Transparency* (pp. 610–623). *Association for Computing Machinery*.
  https://doi.org/10.1145/3442188.3445922

- Bender, E. M., & Friedman, B. (2018). Data statements for natural language processing: Toward
  mitigating system bias and enabling better science. *Transactions of the Association for
  Computational Linguistics*, 6, 587–604. https://doi.org/10.1162/tacl_a_00041

- Marcus, G., & Davis, E. (2019). *Rebooting AI: Building artificial intelligence we can trust*.
  Pantheon Books.

- Mitchell, M. (2019). *Artificial intelligence: A guide for thinking humans*. Farrar, Straus and Giroux.

- Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E.,
  Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In *Proceedings of the
  Conference on Fairness, Accountability, and Transparency* (pp. 220–229). *Association for
  Computing Machinery*. https://arxiv.org/abs/1810.03993


### Projects

__1. Evaluate AI "Understanding" Through the Chinese Room Analogy__

Design a scenario or interactive script inspired by Searle's Chinese Room thought experiment
and test whether a large language model can truly demonstrate understanding—or merely appear
to. You might simulate conversation and analyze its limitations in grasping meaning, reference,
or context.


__2. Compare Human and Machine Analogy-Making__

Recreate a simplified version of Mitchell's Copycat analogy system in Python, and compare its
output to that of a large language model like GPT. Try analogy problems (e.g., "A is to B as C is to ?")
and evaluate the strategies each system uses.


__3. Probe Generalisation Failures in Large Language Models__

Construct a series of tests that require compositional reasoning, such as applying familiar
concepts in unfamiliar combinations ("red cube behind blue pyramid"). Analyze how a language
model performs and where it fails, documenting what this reveals about its internal
representation strategies.


__4. Build a Simple Hybrid AI Model__

Following Marcus's call for hybrid architectures, try to combine symbolic logic with neural
network components. For example, create a rule-based inference engine that uses a neural
network for visual input classification, then reasons about the result symbolically.


__5. Design a Benchmark That Tests World-Embedded Understanding__

Devise a set of questions or tasks that require physical or social reasoning (e.g., understanding
cause and effect, or moral implications in simple stories). Use them to compare how a human
and an AI system interpret the situation, and analyze the difference in grounding.


__6. Investigate Epistemic Humility in AI Output__

Write a program or wrapper for an existing model that tries to assess the confidence of AI
answers--e.g., through calibration methods or self-uncertainty estimation. Then explore when
and how the model should admit uncertainty, and how it compares to human cognitive humility.


__7. Explore Symbolic vs. Statistical Learning on a Toy Problem__

Implement two versions of a learning system: one using symbolic rules (e.g., a Prolog-style
logic system), and one using pattern-matching via statistical methods. Use a small domain
(e.g., family relations) and compare their performance and generalisation on edge cases.


__8. Conduct a Literature Review of Hybrid AI Systems__

Survey recent attempts to build systems that integrate symbolic and neural components.
Summarise their architectures, goals, and results. Critically assess whether they answer
the challenges posed by Marcus and Mitchell regarding causal reasoning, abstraction,
and interpretability.


__9. Visualise the Lack of Causal Models in LLMs__

Design a set of simple physical reasoning problems (e.g., "What happens if you push the
box off the table?") and ask a language model to explain. Compare this with basic
simulations or diagrammatic reasoning. Highlight where causal inference is missing
or inconsistent.


__10. Analyze the Philosophical Assumptions Behind a Modern AI System__

Pick an AI system or service (e.g., ChatGPT, DALL·E, self-driving software) and analyse
what assumptions about intelligence, learning, or knowledge it encodes. Relate your
analysis to ideas from Davidson, Searle, or Mitchell, and evaluate how well the system
aligns with or departs from human cognition.
