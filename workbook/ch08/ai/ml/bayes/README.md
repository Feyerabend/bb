
## Naive Bayes

Naive Bayes classifiers stem from Bayes’ Theorem, formulated by *Thomas Bayes* in the 18th century.
However, the "naive" assumption—treating features as conditionally independent—emerged much later.
The model became practically relevant in the 1950s and 1960s with the development of early machine
learning algorithms. Despite its simplicity, it gained popularity in *text classification*,
*spam filtering*, and other probabilistic inference tasks, especially in the 1990s with the growth
of digital text processing.

Naive Bayes is a *probabilistic classifier* based on Bayes’ Theorem:

```
P(C | X) = (P(X | C) * P(C)) / P(X)
```

Where:
- `C` is a class label.
- `X = (x₁, x₂, ..., xₙ)` is the feature vector.
- `P(C | X)` is the posterior probability of class `C` given the features.
- `P(X | C)` is the likelihood.
- `P(C)` is the prior probability of class `C`.
- `P(X)` is the evidence (a normalization constant).

The "naive" part comes from assuming that all features `xᵢ`
are *conditionally independent* given the class `C`:

```
P(X | C) = ∏ P(xᵢ | C)
```

This simplification allows efficient learning and prediction.

#### Training and Prediction

1. *Training* involves estimating:
   - Class priors `P(C)`.
   - Feature likelihoods `P(xᵢ | C)`, using frequency counts or
     distributions (e.g. Gaussian for continuous features).

2. *Prediction*:
   - For a new input `X`, compute the posterior for each class
     and choose the one with the highest score.

#### Common Variants

- *Multinomial Naive Bayes*: Suitable for discrete features like word counts in documents.
- *Bernoulli Naive Bayes*: Assumes binary features (word present or not).
- *Gaussian Naive Bayes*: Assumes features are continuous and normally distributed.

#### Use Cases

- *Spam detection*: Classify emails as spam/ham.
- *Text classification*: News categorisation, sentiment analysis.
- *Medical diagnosis*: Predict disease likelihood from symptoms.
- *Document classification*: Fast, scalable method even with large vocabularies.

Naive Bayes is particularly effective when:
- The independence assumption roughly holds.
- There is a large number of features but relatively few training samples.

The code often uses *Laplace smoothing*: E.g. in the case of spam Laplace smoothing adds 1 to
all word counts to avoid zero probabilities for unseen words during prediction.  
This ensures that every word has a non-zero chance of occurring, stabilising the model
especially for small datasets.
