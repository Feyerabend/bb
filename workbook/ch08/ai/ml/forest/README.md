
## Random Forest

Random Forest is an ensemble learning method that operates by constructing a
multitude of [decision trees](./../dtree/) during training and outputting
the mode of the classes (classification) or mean prediction (regression)
of the individual trees. It combines the principles of bagging (bootstrap
aggregating) and random feature selection to create a diverse set of trees,
reducing overfitting and improving generalisation.


#### 1. Decision Trees

Each tree in the forest is built using a subset of the training data, sampled
with replacement (bootstrap sampling). The trees are grown deep, with little
to no pruning, ensuring low bias but high variance, which is later mitigated
by averaging multiple trees.

#### 2. Feature Randomness

At each split in a tree, the algorithm considers only a random subset of features
(typically the square root of the total number of features for classification).
This decorrelates the trees, making the ensemble more robust to noise.

#### 3. Splitting Criteria: Gini Impurity & Entropy

- *Gini Impurity*: Measures the probability of misclassifying a randomly chosen
  element if it were labeled according to the class distribution in the subset.
  A Gini index of 0 indicates perfect purity. Mathematically, it is defined as:  
  $Gini = 1 - \sum_{i=1}^C (p_i)^2$, where $p_i$ is the probability of class $i$.

- *Entropy (Information Gain)*: Quantifies the disorder in a dataset. Splits are
  chosen to maximize information gain, which is the reduction in entropy. Entropy
  is calculated as:  
  $Entropy = -\sum_{i=1}^C p_i \log_2(p_i)$.  
  A split with zero entropy means all elements belong to one class.

#### 4. Aggregation

For classification, the final prediction is the majority vote of all trees. For
regression, it is the average of all tree predictions. This aggregation reduces
variance without increasing bias.


### Examples

1. *Medical Diagnosis*: Predicting disease presence based on patient metrics
   (e.g., diabetes, cancer) by learning from historical data with multiple biomarkers.  
2. *Finance*: Credit scoring to assess loan eligibility by analyzing income, transaction
   history, and other financial features.  
3. *E-commerce*: Recommender systems to suggest products by leveraging user behavior and
   purchase history.  
4. *Remote Sensing*: Land cover classification using satellite imagery data with spectral
   and spatial features.  
5. *Industrial Quality Control*: Detecting defective products by analyzing sensor data from
   manufacturing lines.


### Pros and Cons

*Strengths*:  
- Handles high-dimensional data well.  
- Resistant to overfitting due to ensemble averaging.  
- Can model non-linear relationships without feature scaling.  

*Weaknesses*:  
- Less interpretable than single decision trees.  
- Slower prediction time compared to simpler models (e.g., linear regression).  
- May struggle with very high-cardinality categorical features.
