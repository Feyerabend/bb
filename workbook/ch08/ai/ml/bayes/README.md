
## Naive Bayes

Naive Bayes classifiers stem from Bayes’ Theorem, formulated by *Thomas Bayes* in the 18th century.
However, the "naive" assumption—treating features as conditionally independent—emerged much later.
The model became practically relevant in the 1950s and 1960s with the development of early machine
learning algorithms. Despite its simplicity, it gained popularity in *text classification*,
*spam filtering*, and other probabilistic inference tasks, especially in the 1990s with the growth
of digital text processing.

Naive Bayes is a *probabilistic classifier* based on Bayes’ Theorem:

```math
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

```math
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

### Naive Bayes Variants

| Variant             | Input Type         | Feature Model                        | Common Use Case                |
|---------------------|--------------------|--------------------------------------|--------------------------------|
| *Multinomial NB*  | Discrete counts     | Frequencies of features (e.g. word counts) | Text classification, spam filtering |
| *Bernoulli NB*    | Binary features     | Presence/absence of features         | Binary text features, document classification |
| *Gaussian NB*     | Continuous values   | Assumes features follow a Gaussian distribution | Sensor data, medical measurements, numerical features |

- *Multinomial* is best when feature frequency matters (e.g., "cheap" appearing 3 times).
- *Bernoulli* is suitable when only presence or absence is relevant (e.g., "contains the word 'buy'?").
- *Gaussian* fits continuous domains where values follow roughly normal distributions.


### Projects

Below is a list of practical and exploratory projects suitable for you to learn about
Naive Bayes classifiers. These projects emphasise implementation, comparison, analysis,
and visualisation.

#### 1. Build a Spam Filter
- Implement Multinomial Naive Bayes from scratch.
- Use a dataset of emails labeled "spam" or "ham".
- Evaluate accuracy, precision, recall, and F1-score.
- Bonus: compare performance with scikit-learn's implementation.

#### 2. Compare Naive Bayes Variants
- Apply Multinomial, Bernoulli, and Gaussian Naive Bayes on the same dataset.
- Use different encodings (e.g., count, binary, normalized floats).
- Visualize accuracy and decision boundaries (for 2D data).
- Analyze sensitivity to feature scaling and preprocessing.

#### 3. Sentiment Analysis on Movie Reviews
- Use the IMDb or Rotten Tomatoes dataset.
- Train a Multinomial Naive Bayes to classify reviews as positive or negative.
- Try stemming, stopword removal, and different tokenizations.
- Optional: Use n-grams instead of just unigrams.

#### 4. Naive Bayes for Image Classification
- Use Gaussian Naive Bayes on small grayscale datasets (e.g., digits from MNIST).
- Visualize per-class Gaussian parameters (mean images).
- Compare with logistic regression or k-NN.

#### 5. Visualise Decision Boundaries
- Generate synthetic 2D data (e.g., `make_classification` or `make_blobs`).
- Train a Gaussian Naive Bayes model.
- Plot decision regions and class means.
- Show how class priors and feature variance affect boundaries.

#### 6. Bayes vs. Non-Bayes
- Compare a Naive Bayes classifier with non-probabilistic classifiers like:
  - k-Nearest Neighbors
  - Decision Trees
  - Support Vector Machines
- Use the same preprocessing pipeline.
- Write a report analysing when Naive Bayes performs surprisingly well (e.g., with sparse data).

#### 7. Effect of Feature Independence Violation
- Create a synthetic dataset where features are explicitly dependent (e.g., XOR patterns).
- Train Naive Bayes and compare performance with a model that handles dependencies (e.g., decision tree).
- Reflect on the limits of the "naive" assumption.

#### 8. Topic Classification from News Articles
- Use the 20 Newsgroups dataset.
- Preprocess with TF or TF-IDF.
- Classify articles into categories (e.g., politics, sports).
- Bonus: rank most indicative words per category based on conditional probabilities.

#### 9. Interactive Naive Bayes Demo (Web App)
- Build a simple browser-based interface using JavaScript or Python (e.g., with Flask).
- Allow users to enter a sentence or upload data.
- Display predicted class, top contributing words, and feature likelihoods.
- Optional: toggle smoothing, priors, or feature encodings interactively.

#### 10. Real-time Classifier on Sensor Data
- Connect a microcontroller or use time-series datasets (e.g., accelerometers).
- Classify motion or activity using Gaussian Naive Bayes.
- Deploy in a low-resource environment to demonstrate computational efficiency.
