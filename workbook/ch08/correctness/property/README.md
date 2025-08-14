
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
    - `trad_sort.py`: Tests a sorting function with specific unit tests for basic functionality,
      edge cases, duplicates, and negative numbers using Python's `sorted` function.
    - `hyp_sort.py`: Uses Hypothesis for property-based testing, verifying general sorting properties
      (ordering, permutation, length, idempotence) across random integer lists.

- [str](./str/) -- These scripts use Hypothesis for PBT on Python strings, checking
  associativity, identity, length additivity, reversal involution, and substring preservation
  with random inputs. Aim: Demonstrate PBT's superiority for robust, property-driven validation
  vs. manual examples. Also requires installation of pytest.

- [instr](./instr/) -- An example of testing a (custom) function with PBT. Also some logics
  for background. The `instr.py` program implements the `INSTR` function, which finds the 1-based
  position of a substring within a string from a specified start, returning 0 if not found,
  and handles edge cases like empty strings and invalid starts. It includes unit tests for
  specific scenarios and property-based tests using Hypothesis to verify general properties
  such as substring matching and position constraints.

- [bst](./bst/) -- A Python implementation of a simplified Binary Search Tree (BST) uses
  a set to store values and is tested with property-based testing via Hypothesis to ensure
  invariants like sorted in-order traversal, correct size, membership, and completeness
  across diverse random inputs. Logging in JSON Lines format captures test inputs and
  BST states for debugging, with integration demonstrated for pytest, though the BST
  implementation avoids traditional tree structure complexity. An incomplete (think project)
  HTML file suggests potential for visualising test results, highlighting the automation,
  robustness, and debugging benefits of property-based testing for data structures.

- [stats](./stats/) -- The `stats.py` and `shrink.py` programs implement a custom
  property-based testing framework in Python, using `StatisticalTestRunner` to evaluate
  code invariants with random inputs, enhanced by statistical analysis like success rates,
  confidence intervals, and failure patterns. They include strategies for generating
  integers and lists, with `shrink.py` adding sophisticated shrinking mechanisms to
  minimise failing test cases, demonstrated through testing a buggy sorting property
  that fails on duplicates and a correct one that handles them properly. We further
  explain the framework’s statistical approach, its educational purpose abstaining from
  using Hypothesis, and provides guidance on implementing PBT manually, emphasising
  falsifiability, adaptivity, and detailed reporting for robust testing.

- [mmorph](./mmorph/) -- A framework for metamorphic testing, which verifies software
  by checking relational properties between transformed inputs and outputs without
  needing exact oracles. It includes strategies for generating random test data
  (integers, floats, lists, etc.), defines metamorphic relations for domains like
  sorting, math, and strings, and runs automated test suites to detect bugs. Demonstrates
  usage with examples on correct/buggy sorters, mathematical functions, and string
  processors, emphasising extensibility for complex algorithms.
