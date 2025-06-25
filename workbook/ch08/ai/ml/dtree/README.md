
## Decision Trees

Decision trees are one of the most intuitive and widely-used machine learning algorithms,
representing decisions and their possible consequences in a tree-like structure. At their
core, they mirror how humans naturally make decisions by asking a series of yes/no questions
until reaching a conclusion.

A decision tree starts with a root node representing the entire dataset, then splits the data
based on feature values that best separate different outcomes. Each internal node represents
a decision point (like "Is age > 30?"), each branch represents the outcome of that decision,
and each leaf node represents a final prediction or classification.

The algorithm works by selecting the feature and split point that creates the most homogeneous
subgroups. For classification problems, this often means maximising information gain or
minimising Gini impurity. For regression, it typically minimises mean squared error.

*Splitting Criteria*: The algorithm evaluates different ways to split the data at each node.
Common measures include:
- Information gain (based on entropy reduction)
- Gini impurity (probability of misclassifying a randomly chosen element)
- Chi-square test for categorical variables

*Stopping Conditions*: Trees stop growing when they reach certain criteria like maximum depth,
minimum samples per leaf, or when further splits don't improve the model significantly.

*Pruning*: Since trees can easily overfit by memorising training data, pruning removes branches
that don't contribute meaningfully to generalisation.


### Relationship to Other Algorithms

Decision trees serve as building blocks for several powerful ensemble methods. [*Random Forests*](./../forest/)
create hundreds of decision trees on random subsets of data and features, then average their predictions to
reduce overfitting and improve accuracy. [*Gradient Boosting*](./../boost/) methods like XGBoost and LightGBM
sequentially build trees where each new tree corrects errors from previous ones.

Unlike linear models that assume relationships can be captured with straight lines, decision trees naturally
handle non-linear relationships and interactions between features. They contrast with neural networks in their
interpretability--you can easily trace the exact path of decisions that led to any prediction.

Compared to [k-nearest neighbours](./../knn/), decision trees don't require storing all training data and
make predictions quickly. Unlike [Support Vector Machines](./../svm/), they don't assume any particular
distribution of data and can handle both numerical and categorical features without preprocessing.


### Advantages and Applications

Decision trees excel in scenarios requiring interpretability. In healthcare, doctors can follow the tree's
logic to understand why a model recommends a particular diagnosis. In finance, loan officers can explain
to customers exactly which factors led to credit decisions. Marketing teams use them to segment customer
based on clear, actionable criteria.

They handle missing values gracefully, require minimal data preparation, and can capture complex patterns
like "customers under 25 OR customers over 65 with high income are likely to buy this product."


### Limitations and Trade-offs

Single decision trees tend to overfit, creating overly complex models that perform poorly on new data.
They're also unstable--small changes in training data can result in very different trees. They struggle
with linear relationships that would be easily captured by linear regression, and can be biased toward
features with more levels when dealing with categorical variables.

The rectangular decision boundaries created by trees can be inefficient for problems where diagonal
or curved boundaries would be more natural.


### Modern Context and Evolution

While simple decision trees have limitations, they remain foundational to modern machine
learning. The most successful competition algorithms on platforms like Kaggle are often
ensemble methods built on decision trees. Libraries like scikit-learn, XGBoost, and LightGBM
have made sophisticated tree-based methods accessible to practitioners.

Recent developments include differential privacy techniques for trees, interpretable boosting
methods, and neural network architectures that incorporate tree-like decision structures.

Decision trees represent a sweet spot in machine learning--powerful enough to capture complex
patterns, yet simple enough that humans can understand and trust their decisions. This
combination of effectiveness and interpretability ensures their continued relevance across
industries and applications.

