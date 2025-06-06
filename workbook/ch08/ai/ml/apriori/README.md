
## Apriori Algorithm

This code implements a browser-based visualisation of the *Apriori* algorithm, a classic algorithm
in data mining for discovering frequent itemsets in a transaction database (for example, market basket
analysis as here). The HTML/CSS/JavaScript-based application lets you experiment with support thresholds
and observe how frequent itemsets are found.


## What Is It?

The Apriori algorithm is used to mine frequent itemsets (sets of items that often appear together in
transactions) and can be extended to generate association rules. It relies on the Apriori Principle:

> If an itemset is frequent, all of its subsets must also be frequent.

Conversely, if a candidate itemset is infrequent, none of its supersets can be frequent. This allows
pruning of the search space.


## Mathematical Foundations

Let:
- \($ I = \{ i_1, i_2, \dots, i_n \} $\): set of all items.
- \($ D = \{ T_1, T_2, \dots, T_m \} $\): set of transactions, where each \($ T_i \subseteq I $\).
- An itemset \($ X \subseteq I $\) is frequent if its support exceeds a user-defined threshold.

Support of itemset \($ X $\):
```math
\text{support}(X) = \frac{|\{ T \in D \mid X \subseteq T \}|}{|D|}
```


## Apriori Algorithm

1. Generate 1-itemsets and count support.
2. Prune those below `minSupport`.
3. Generate k-itemsets from previous (k−1)-itemsets (by joining and filtering).
4. Repeat until no new itemsets remain.

