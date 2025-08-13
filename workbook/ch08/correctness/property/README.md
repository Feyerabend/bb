
> [!IMPORTANT]  
> Many of the examples are given in Python which requires installation of "Hypothesis"

## Property-Based Testing

Property-based testing occupies a hybrid position between conventional software testing 
and fully formal verification.

Like traditional testing, it executes the program on specific inputs to check whether it
behaves as expected. The key difference is that, instead of manually choosing a handful of
representative cases, property-based testing generates a wide variety of inputs--often randomly
or according to systematic rules--to explore the program’s behaviour over a much larger
portion of the input space. This approach still relies on sampling rather than exhaustively
covering all possible cases, so it cannot provide absolute guarantees; at best, it can *expose
faults with high probability*.

At the same time, property-based testing shares important characteristics with *formal
verification*. The process begins by stating general properties or invariants that the
program should satisfy for all valid inputs. This specification-driven mindset is the
same starting point as a formal proof: the developer expresses requirements in abstract,
universal terms rather than as a list of examples. In fact, in some workflows, property-based
testing serves as a preliminary step before formal verification--allowing developers to
validate that a property is reasonable and that no obvious counterexamples exist before
investing in a proof. When a test fails, the testing framework often produces a minimal
counterexample, much like a proof assistant returning a countermodel.

In practice, this combination makes property-based testing a flexible tool. It retains the
pragmatic immediacy of testing--quick execution and direct feedback--while nudging developers
toward the formal methods mindset of reasoning about entire domains of inputs. This hybrid
nature explains why it is equally at home in robust traditional QA pipelines and in
verification-oriented development processes.

Property-Based Tests (PBTs) introductions:

- [simple](./simple/) -- Where you could start exploring the difference between a traditional
  approach, and the property-based approach to testing. The examples are highly transparent,
  but the PBT requires installing Hypothesis.

- [instr](./instr/) -- An example of testing a (custom) function with PBT. Also some logics
  for background.

- [bst](./bst/) -- Some more properties tested for a BST implementation. Some ideas on
  illustrating the underlying testing scheme for PBT are added.

- [stats](./stats/) -- Dig deeper into implementation, as it avoids Hypothesis. Also how
  more customisation can be added for PBT.

