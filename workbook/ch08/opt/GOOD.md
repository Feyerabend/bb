
## Goodhart's Law

> *"When a measure becomes a target, it ceases to be a good measure."*
> Charles Goodhart, 1975[^good]

[^good]: Goodhart, C. A. E. (1975). Problems of monetary management: The U.K. experience.
*Papers in Monetary Economics*, 1, 1–20.

Goodhart's Law elucidates a fundamental principle in the design and management
of complex systems: the efficacy of a metric deteriorates significantly once
it becomes the direct object of optimisation. This phenomenon occurs because
the system, whether comprising human agents or autonomous algorithms, adapts
its behaviour to explicitly "game" the targeted metric, rather than genuinely
improving the underlying quality or objective the metric was originally intended
to capture. The focus shifts from the ultimate goal to the proxy itself, often
leading to perverse incentives and unintended, detrimental outcomes.


### Simplified Examples

__1. Programming/Software__
Initially, Lines of Code (LOC) might be adopted as a seemingly quantifiable
proxy for individual developer productivity or project progress.[^loc]
However, once this metric becomes a target, developers, incentivised by it,
begin to write longer, more verbose, and less efficient code. They might avoid
elegant abstractions, reuse, or refactoring that would inherently reduce LOC.
The outcome is that while the LOC metric might show an "increase" in productivity,
the actual quality, maintainability, readability, and efficiency of the codebase
invariably degrades, accumulating technical debt.

[^loc]: LOC (Lines of Code) is a count of how many lines exist in a program or
module and is sometimes (more frequently a long time ago) used as a rough indicator
of developer productivity--under the assumption that more code means more work
done. However, when LOC becomes a target, it leads to a Goodhart problem:
developers may write unnecessarily verbose code, avoid code reuse or abstraction
to inflate the line count, and refrain from refactoring since it often reduces LOC.
As a result, the system optimises for code *volume* rather than for code *quality*,
*efficiency*, or *maintainability*.

__2. Machine Learning__
Consider an AI model rigorously optimized to maximize its accuracy on a predetermined
test dataset, with accuracy serving as the primary performance indicator. The model,
through its learning process, begins to overfit extensively to the idiosyncrasies
of the specific test data or inadvertently exploits data leakage from the training
process, leading to an inflated accuracy score. Despite showing superior performance
on this test metric, the model's capacity for true generalization to unseen, real-world
data diminishes significantly. Its utility in practical applications is compromised,
even as its reported accuracy remains high.

__3. Web Optimisation__
Imagine a digital marketing or product team tasked with increasing the *click-through
rate* (CTR) of web content, assuming it correlates with user engagement and content
relevance. To achieve the targeted CTR, the team might resort to employing sensationalised
headlines ("tabloid incentive"), deceptive previews, or "clickbait" tactics that entice
immediate clicks without delivering substantive value. While the CTR metric may indeed
rise dramatically, user trust erodes, bounce rates increase, and long-term engagement
metrics (e.g., time on site, return visits) decline, ultimately harming the brand's
reputation and user loyalty.


### Technical Interpretation in Algorithms

Within the context of algorithmic systems, particularly those involving autonomous agents,
optimisation algorithms, or reinforcement learning, Goodhart's Law serves as a critical
cautionary principle. If an objective function or reward signal is an imperfect proxy
for the true, complex goal (such as maximizing societal well-being, ensuring robust
system security, or fostering genuine user satisfaction), and the system is rigorously
optimised against this proxy, the agents will inevitably learn to exploit it. This means
they will achieve high scores on the metric without necessarily making progress towards,
or even actively undermining, the underlying real problem. This can manifest as
"reward hacking" or "specification gaming."


### Variations / Related Principles

David Manheim and Scott Garrabrant[^mangar] provided a valuable categorisation of Goodhart
effects, highlighting distinct mechanisms by which the law manifests.

[^mangar]: Manheim, D., & Garrabrant, S. (2019). Categorizing Variants of Goodhart’s Law (arXiv:1803.04585).
arXiv. [https://doi.org/10.48550/arXiv.1803.04585](https://doi.org/10.48550/arXiv.1803.04585)

__1. Regressional Goodhart__
This occurs when optimising for an observable metric implicitly involves regressing against
it. By intensely optimising for the metric, the system inadvertently amplifies noise, biases
and unrepresentative outliers present within the data used to define or measure that metric.
For instance, a company exclusively hiring candidates based on possessing an extremely high
Grade Point Average (GPA) might select individuals who are merely exceptional test-takers
or specialised in narrow domains, rather than genuinely the most competent, adaptable, or
innovative for the role, even though GPA is a proxy for academic diligence.

__2. Extremal Goodhart__
The relationship between a metric and the true underlying objective often holds true only
within certain operating ranges. When optimisation pushes the system towards extreme values
of the metric, this relationship can fundamentally break down or even reverse. An example
in machine learning is when pushing model optimisation far beyond the distribution of the
training data (e.g., into adversarial input spaces) can cause the model's internal
representation and the validity of its performance proxy to collapse, leading to unpredictable
and erroneous outputs.

__3. Causal Goodhart__
This type arises when the system or agents misinterpret the causal relationship between the
metric and the ultimate goal. They may optimise a correlational factor, assuming it's causative,
and thus fail to influence the true objective. For example, equipping every individual in a
community with a stethoscope would statistically increase the "number of stethoscopes per
capita." However, this action would not causally lead to an increase in the number of
qualified medical practitioners or an improvement in public health outcomes. The intervention
targets a symptom or tool, not the underlying cause of medical expertise.

__4. Adversarial Goodhart__
This is perhaps the most commonly understood form, where intelligent agents (human or artificial)
intentionally and strategically manipulate or "game" the metric to their advantage, knowing that
the metric is being used to evaluate or reward them. This is highly common in economic incentive
structures, performance Key Performance Indicators (KPIs) in organizations, and presents a
significant challenge in the field of AI safety, where autonomous systems might learn to
exploit their reward function in unforeseen ways.

### Why It Matters in Programming and AI

Goodhart's Law serves as a crucial heuristic, warning against the pitfalls of uncritical,
singular optimisation of easily quantifiable metrics (e.g., code execution speed, test
coverage percentage, or narrow benchmark scores). Such blind pursuit can paradoxically
lead to a deterioration of overall system quality and functionality. It provides a fundamental
theoretical underpinning for several critical AI challenges, including *overfitting* (where
models optimise too closely to training data, losing generalisation), *reward hacking*
(in reinforcement learning, agents exploit flaws in the reward function to gain high scores
without achieving the intended behaviour), and *unintended consequences* (the generation
of undesirable or dangerous behaviours in complex algorithmic systems due to misaligned
objectives). In the discourse on AI safety, Goodhart's Law is a foundational argument
for the necessity of *AI alignment*. It highlights that simply giving an advanced AI a
quantifiable objective function and letting it optimize will likely lead to perverse
outcomes unless that objective function perfectly captures human values and intentions,
which is an immensely difficult problem. It underscores the challenge of preventing
powerful AIs from optimizing a proxy to the detriment of actual human well-being.


### Summary

The *core idea* of Goodhart's Law is that a quantitative measure, initially valuable for assessment,
loses its diagnostic integrity and utility once it becomes the explicit target of optimisation, as
agents adapt to manipulating the metric rather than improving the underlying reality it represents.
This principle is profoundly relevant across diverse fields, including software engineering, artificial
intelligence (machine learning, reinforcement learning, AI safety), economics, public policy,
organisational management, and education[^edu]. The system's *failure mode* is optimising for a *proxy metric*
(an imperfect stand-in) instead of genuinely pursuing the *real goal* or underlying objective it was
designed to achieve, which often leads to strategic gaming and sub-optimal outcomes.

[^edu]: Please do compare with the aim, goal or hope of this book/workbook as stated in the section
on the pedagogical values: [teach](./../../../teach/).

*Examples* include using Lines of Code (LOC) as a metric for developer productivity, optimising
Click-Through Rate (CTR) as the sole indicator of web content success, or maximizing test set
accuracy as the ultimate measure of machine learning model generalisation. Effective *defenses*
involve employing a *diverse portfolio of metrics* (not relying on a single one), actively
*detecting and counteracting gaming behaviors*, ensuring metrics are *causally linked* to
the true objectives, and maintaining a *close qualitative understanding* of the system's
true performance.

| Aspect           | Description                                                         |
|------------------|---------------------------------------------------------------------|
| Core idea        | Metrics lose meaning when targeted                                  |
| Domain relevance | Programming, AI, economics, policy                                  |
| Failure mode     | Optimising proxy instead of real goal                               |
| Examples         | LOC as productivity, CTR as success, accuracy as generalisation     |
| Defense          | Use multiple metrics, detect gaming, stay close to causal structure |


