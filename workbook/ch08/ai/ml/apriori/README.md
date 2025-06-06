
## Apriori Algorithm

This code implements a browser-based visualisation of the *Apriori* algorithm, a classic algorithm
in data mining for discovering frequent itemsets in a transaction database (for example, market basket
analysis as here). The HTML/CSS/JavaScript-based application lets you experiment with support thresholds
and observe how frequent itemsets are found.

The Apriori algorithm is used to mine frequent itemsets (sets of items that often appear together in
transactions) and can be extended to generate association rules. It relies on the Apriori Principle:

> If an itemset is frequent, all of its subsets must also be frequent.

Conversely, if a candidate itemset is infrequent, none of its supersets can be frequent. This allows
pruning of the search space.


### Mathematical Foundations

Let:
- $I = \{ i_1, i_2, \dots, i_n \}$: set of all items.
- $D = \{ T_1, T_2, \dots, T_m \}$: set of transactions, where each $T_i \subseteq I$.
- An itemset $X \subseteq I$ is frequent if its support exceeds a user-defined threshold.

Support of itemset $X$:
```math
\text{support}(X) = \frac{|\{ T \in D \mid X \subseteq T \}|}{|D|}
```


### The Algorithm Simplified

1. Generate 1-itemsets and count support.
2. Prune those below `minSupport`.
3. Generate k-itemsets from previous (k−1)-itemsets (by joining and filtering).
4. Repeat until no new itemsets remain.





### FP-Growth: Definitions and Notation

Let:
- $\mathcal{D}$ be a transaction database with N transactions.
- $I = \{i_1, i_2, \ldots, i_m\}$ be the set of m distinct items.
- $\sigma(i)$ denote the support count of item $i$, i.e., number
  of transactions containing $i$.
- $\text{minsup} \in (0,1]$ be the minimum support threshold (fraction).
- An itemset is a subset $X \subseteq I$.
- $\text{support}(X) = \frac{|\{ T \in \mathcal{D} \mid X \subseteq T \}|}{N}$

Apriori uses a generate-and-test strategy in cadidate generation:
- At level $k$, it generates candidate itemsets $C_k$ of size $k$,
  and scans the database to count their supports.
- Then it filters out infrequent ones to get $L_k$, the frequent
  itemsets of size $k$.

Cost:
- Candidate explosion:
    - Worst-case number of candidates:
        $\sum_{k=1}^{m} \binom{m}{k} = 2^m - 1$
    - Though pruning based on support limits this in practice,
      it’s still exponential in $m$ when $\text{minsup}$ is low.
- Database scans:
    - Requires $k$ full scans for discovering all $L_1, L_2, …, L_k$.
- Support counting cost per scan:
    - For each candidate $X \in C_k$, check inclusion in each
      transaction $T \in \mathcal{D}$, i.e., $\mathcal{O}(|C_k| \cdot N)$
- Total time complexity (approx):
    $\mathcal{O}\left(\sum_{k=1}^K |C_k| \cdot N \cdot k \right)$


### FP-Growth: Divide-and-Conquer via FP-tree

FP-Growth avoids candidate generation by compressing the database
into a prefix tree (FP-tree) and mining recursively.

FP-tree construction:
- Single scan for frequency counts.
- Second scan to build tree of only frequent items (in support-descending order).
- Nodes store item name, count, and pointers.
- Common prefixes are shared, drastically reducing storage size.

Cost:
- Tree size:
- Let $\text{avg\_prefix\_len}$ be average number of frequent items per transaction.
- Total number of nodes $\leq N \cdot \text{avg\_prefix\_len}$
- Mining cost (recursive pattern growth):
- For each item $i$, extract conditional pattern base (all prefix paths ending in $i$).
- Build a conditional FP-tree and recurse.
- Total time complexity (approx):
    $\mathcal{O}(N \cdot \text{avg\_prefix\_len} + \text{#conditional_trees})$
- Number of conditional trees is $\leq \text{#frequent items}$, but recursion can go deep.
- Space complexity:
    $\mathcal{O}(N \cdot \text{avg\_prefix\_len})$
- Much lower than storing all $C_k$ in Apriori.



### Comparison Table

| Aspect                    | Apriori                      | FP-Growth                  |
|---------------------------|------------------------------|----------------------------|
| Strategy                  | Generate-and-test            | Divide-and-conquer         |
| Candidate Generation      | Explicit                     | None                       |
| Database Scans            | $\\geq k$                    | 2                          |
| Time Complexity           | $O(∑ₖ \|Cₖ\| ⋅ N ⋅ k)$          | $O(N ⋅ avg_prefix_len + T)$|
| Memory Use                | High (stores all $C_k$)      | Low (compact tree)         |
| Performance on Sparse Data| Acceptable                   | Excellent                  |
| Performance on Dense Data | Slow (many $C_k$)            | Much faster                |



### Mathematical Insight

- FP-Growth performs better because it leverages prefix sharing, turning the
  exponential number of possible itemsets into a linear traversal of a shared
  tree structure.

- The FP-tree is a compressed representation of the database, exploiting the
  downward closure property (if X is frequent, all subsets are frequent), just
  like Apriori, but without enumerating subsets.

