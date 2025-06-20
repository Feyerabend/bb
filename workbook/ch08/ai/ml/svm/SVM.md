
## Support Vector Machines

Support Vector Machines (SVMs) are powerful supervised learning algorithms, primarily
used for classification and regression tasks. Developed by Vladimir Vapnik and his
colleagues in the 1990s, SVMs became one of the most popular machine learning methods
due to their strong theoretical foundations and excellent performance on many real-world
problems. However, interest in SVMs has declined in recent years.

The core idea behind SVMs is to find an optimal hyperplane that best separates data points
belonging to different classes in a high-dimensional feature space.

Imagine you have a dataset with two classes of points, say red and blue, scattered on a 2D plane.
If these points are linearly separable, you can draw a straight line to divide them. However,
there might be many such lines. The SVM aims to find the *best* line. This "best" line is the
one that maximises the margin between the closest data points of each class. These closest
data points are called *support vectors*.

The margin is the distance between the hyperplane and the nearest data point from either class.
A larger margin generally leads to better generalisation performance, meaning the model is less
likely to misclassify unseen data.


### Mathematical Formulation

Given a dataset of $n$ training samples $(x_1, y_1), ..., (x_n, y_n)$, where $x_i \in \mathbb{R}^d$
is a $d$-dimensional feature vector and $y_i \in \{-1, 1\}$ is the class label.

The goal is to find a hyperplane defined by the equation:
$w \cdot x + b = 0$

where:
* $w$ is the weight vector, orthogonal to the hyperplane.
* $x$ is a data point.
* $b$ is the bias (or intercept).

For a correctly classified sample, we want:
* $w \cdot x_i + b \ge 1$ if $y_i = 1$
* $w \cdot x_i + b \le -1$ if $y_i = -1$

These two conditions can be combined into a single inequality:
$y_i (w \cdot x_i + b) \ge 1$

The points that satisfy $y_i (w \cdot x_i + b) = 1$ are the support vectors. The distance from
the origin to the hyperplane is $|b| / \|w\|$, and the margin is $2 / \|w\|$.

To maximise the margin, we need to minimize $\|w\|^2$ (which is equivalent to minimizing $\|w\|$).
This can be formulated as a constrained optimisation problem:

*Minimize:* $f(w) = \frac{1}{2} \|w\|^2$

*Subject to:* $y_i (w \cdot x_i + b) \ge 1$ for all $i = 1, ..., n$

This is a convex optimisation problem that can be solved using techniques like Lagrange multipliers.
The solution for $w$ and $b$ defines the optimal hyperplane.


### Soft Margin SVM

The above formulation assumes that the data is perfectly linearly separable. In real-world scenarios,
data often contains noise or overlaps, making perfect separation impossible. To address this, the
*Soft Margin SVM* was introduced.

Soft Margin SVM allows for some misclassifications by introducing slack variables, $\xi_i \ge 0$,
for each data point. The constraint becomes:
$y_i (w \cdot x_i + b) \ge 1 - \xi_i$

If $\xi_i > 0$, the data point is either within the margin or on the wrong side of the hyperplane.
The optimisation problem now includes a penalty for misclassifications:

*Minimize:* $\frac{1}{2} \|w\|^2 + C \sum_{i=1}^n \xi_i$

*Subject to:*
* $y_i (w \cdot x_i + b) \ge 1 - \xi_i$
* $\xi_i \ge 0$

Here, $C > 0$ is a regularization parameter.
* A small $C$ allows for a larger margin but also more misclassifications (higher bias, lower variance).
* A large $C$ enforces a smaller margin to reduce misclassifications (lower bias, higher variance).


### The Kernel Trick

One of the most significant innovations in SVMs is the *Kernel Trick*. It allows SVMs to effectively handle
non-linearly separable data without explicitly transforming the data into a higher-dimensional space.

The core idea is that in the dual form of the SVM optimization problem, the data points $x_i$ only appear
in dot products, $x_i \cdot x_j$.

The Kernel Trick replaces this dot product with a *kernel function*, $K(x_i, x_j) = \phi(x_i) \cdot \phi(x_j)$,
where $\phi$ is a mapping from the original feature space to a higher-dimensional feature space. We don't need
to explicitly compute $\phi(x)$, only the kernel function $K(x_i, x_j)$. This avoids the computational burden
of working in very high, or even infinite, dimensional spaces.

Common kernel functions include:

1. *Linear Kernel:* $K(x_i, x_j) = x_i \cdot x_j$ (This is equivalent to a standard linear SVM).
2. *Polynomial Kernel:* $K(x_i, x_j) = (x_i \cdot x_j + c)^d$, where $c$ is a constant and $d$ is the degree of the polynomial.
3. *Radial Basis Function (RBF) or Gaussian Kernel:* $K(x_i, x_j) = \exp(-\gamma \|x_i - x_j\|^2)$,
   where $\gamma > 0$ is a hyperparameter. This is one of the most popular and generally effective kernels.
4. *Sigmoid Kernel:* $K(x_i, x_j) = \tanh(\alpha x_i \cdot x_j + c)$, where $\alpha$ and $c$ are constants.

By using different kernel functions, SVMs can learn complex non-linear decision boundaries.


### Other Aspects of SVM

* *Duality:* The SVM optimisation problem can be formulated in a dual form, which is often easier to solve and
  naturally incorporates the kernel trick. The solution in the dual space involves finding Lagrange multipliers.
* *Support Vectors:* Only the support vectors (the data points closest to the hyperplane or those that violate
  the margin constraints) are crucial for defining the decision boundary. All other data points can be removed
  without affecting the hyperplane. This sparseness makes SVMs memory-efficient.
* *Multi-class Classification:* While SVMs are inherently binary classifiers, they can be extended to handle
  multi-class problems using strategies like "One-vs-Rest" (OvR) or "One-vs-One" (OvO).
* *Regression (SVR):* SVMs can also be used for regression tasks (Support Vector Regression). SVR aims to find
  a function that deviates from the true values by a maximum of $\epsilon$, and at the same time is as flat as possible.



### Code `ssvm.py`

The provided starter Python code implements a basic linear (Simple) Support Vector Machine (SVM) from scratch using a
simplified gradient descent-like approach. It does *not* incorporate the sophisticated dual formulation or kernel
tricks found in more advanced SVM implementations.


```python
import random
import numpy as np

# nomalise dataset
def normalize(X):
    X = np.array(X)
    return (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))
```

*`normalize(X)` function:*
* *Purpose:* This function performs min-max normalization on the input data `X`.
* *Mechanism:* It scales each feature (column) in `X` to a range between 0 and 1.
    * `X.min(axis=0)`: Finds the minimum value for each feature (column).
    * `X.max(axis=0)`: Finds the maximum value for each feature (column).
    * `(X - X.min(axis=0))`: Shifts the data so the minimum of each feature becomes 0.
    * `/ (X.max(axis=0) - X.min(axis=0))`: Scales the data so the maximum of each feature becomes 1.
* *Importance:* Normalisation is crucial for many machine learning algorithms, including SVMs,
  especially when features have different scales. It helps prevent features with larger numerical
  ranges from dominating the learning process and can lead to faster convergence and better performance.


```python
class SVM:
    def __init__(self, learning_rate=0.01, lambda_param=0.01, n_iters=1000):
        self.lr = learning_rate
        self.lambda_param = lambda_param
        self.n_iters = n_iters
        self.w = None
        self.b = None
```

*`SVM` Class - `__init__` method:*
* *Purpose:* This is the constructor for the `SVM` class, initialising the hyperparameters and model parameters.
* *`self.lr` (learning_rate):* Controls the step size during the weight and bias updates. A smaller learning rate
  means smaller steps, potentially leading to more stable but slower convergence.
* *`self.lambda_param`:* This is the regularisation parameter, often denoted as $\lambda$ (or the inverse of $C$
  in some SVM formulations). It controls the trade-off between maximising the margin and minimising classification
  errors. A larger `lambda_param` corresponds to a smaller `C`, leading to a wider margin but potentially more
  misclassifications (stronger regularisation).
* *`self.n_iters`:* The number of iterations (epochs) the training algorithm will run. In each iteration, the
  algorithm goes through all training samples.
* *`self.w` (weights):* Initialised to `None`. This will be a NumPy array representing the weight vector of the
  hyperplane. Its dimension will be equal to the number of features in the input data.
* *`self.b` (bias):* Initialized to `None`. This will be a scalar representing the bias term of the hyperplane.

```python
    def fit(self, X, y):
        n_samples, n_features = X.shape
        # Initialize weights and bias
        self.w = np.zeros(n_features)
        self.b = 0.0
        
        for _ in range(self.n_iters):
            for idx in range(n_samples):
                x_i = X[idx]
                condition = y[idx] * (self._predict(x_i) >= 1)
                if condition:
                    # Correct classification
                    self.w = (1 - self.lr * self.lambda_param) * self.w
                else:
                    # Misclassified
                    self.w += self.lr * (y[idx] * x_i - 2 * self.lambda_param * self.w)
                    self.b += self.lr * y[idx]
```

*`fit(self, X, y)` method:*
* *Purpose:* This is the training method of the SVM. It learns the optimal weights (`self.w`) and bias (`self.b`)
  based on the input features `X` and labels `y`.
* *Initialization:*
    * `n_samples, n_features = X.shape`: Gets the number of samples and features from the input data `X`.
    * `self.w = np.zeros(n_features)`: Initializes the weight vector `w` with zeros.
    * `self.b = 0.0`: Initializes the bias `b` to zero.
* *Training Loop:*
    * `for _ in range(self.n_iters):`: This is the outer loop, iterating for a specified number of epochs (`n_iters`).
      In each epoch, the algorithm processes all training samples.
    * `for idx in range(n_samples):`: This is the inner loop, iterating through each training sample `(x_i, y_i)`.
    * `x_i = X[idx]`: Retrieves the current feature vector.
    * `condition = y[idx] * (self._predict(x_i) >= 1)`: This is the core of the update rule, a simplified version of
      the stochastic gradient descent (SGD) update for a linear SVM.
        * `self._predict(x_i)`: Calculates the raw score $w \cdot x_i + b$.
        * `y[idx] * (w \cdot x_i + b)`: This term determines if the point is correctly classified and outside the
          margin (or on the margin).
            * If `y[idx] = 1`, we want $w \cdot x_i + b \ge 1$.
            * If `y[idx] = -1`, we want $w \cdot x_i + b \le -1$, which means $-1 \cdot (w \cdot x_i + b) \ge 1$,
              or $y[idx] \cdot (w \cdot x_i + b) \ge 1$.
        * So, `condition` is `True` if the point is correctly classified and on the correct side of the margin
         (or outside it), and `False` if it's misclassified or inside the margin.
    * *Weight and Bias Updates (Simplified SGD):*
        * *`if condition:` (Correct classification / Outside margin):*
            * `self.w = (1 - self.lr * self.lambda_param) * self.w`: In this case, the main update is a regularisation
              term. It slightly shrinks the weights towards zero. This is a common part of SVM training to prevent
              overfitting (L2 regularisation).
        * *`else:` (Misclassified / Inside margin):*
            * `self.w += self.lr * (y[idx] * x_i - 2 * self.lambda_param * self.w)`: This is the primary gradient
              descent step when a misclassification occurs or a sample is within the margin.
                * `y[idx] * x_i`: This term pushes the hyperplane in the direction that correctly classifies `x_i`.
                  If `y[idx]` is 1, `x_i` is added to `w`; if `y[idx]` is -1, `x_i` is subtracted.
                * `- 2 * self.lambda_param * self.w`: This is the regularization term, penalizing large weights.
            * `self.b += self.lr * y[idx]`: The bias `b` is updated to also help correctly classify `x_i`.
              If `y[idx]` is 1, `b` increases; if `y[idx]` is -1, `b` decreases.

```python
    def _predict(self, x):
        return np.dot(x, self.w) + self.b
```

*`_predict(self, x)` method (private helper):*
* *Purpose:* Calculates the raw score of a single data point `x` relative to the hyperplane.
* *Mechanism:* It computes the dot product of the input feature vector `x` with the weight vector
  `self.w` and then adds the bias `self.b`. This value represents the signed distance of the point from the hyperplane.

```python
    def predict(self, X):
        return [1 if self._predict(x) >= 0 else -1 for x in X]
```

*`predict(self, X)` method:*
* *Purpose:* Predicts the class labels for a given set of input data `X`.
* *Mechanism:* It iterates through each sample `x` in `X`. For each `x`, it calls `self._predict(x)` to get the raw score.
    * If the raw score is greater than or equal to 0, it predicts class `1`.
    * If the raw score is less than 0, it predicts class `-1`.
    * This effectively applies the decision rule: if $w \cdot x + b \ge 0$, classify as 1; otherwise, classify as -1.

```python
# Sample data points with clearer separation
X = [[3.1, 2.5], [1.5, 2.2], [2.3, 3.3], [5.1, 1.6], [4.0, 2.0], [0.5, 0.8]]
y = [1, 1, -1, -1, 1, -1]  # Added more points for better classification

# Normalize the feature matrix
X_normalized = normalize(X)

model = SVM(learning_rate=0.01, n_iters=20000)  # Increased iterations
model.fit(X_normalized, y)
predictions = model.predict(X_normalized)

print("SVM Predictions:", predictions)
```

*Sample Data and Execution:*
* *`X` and `y`:* This defines a small toy dataset. `X` contains 2D data points (features), and `y` contains
  their corresponding binary class labels (1 or -1). The points are chosen to be somewhat linearly separable.
* *`X_normalized = normalize(X)`:* The input features are normalized using the previously defined `normalize`
  function. This is a crucial preprocessing step.
* *`model = SVM(...)`:* An instance of the `SVM` class is created with a learning rate of `0.01` and a significantly
  increased number of iterations (`20000`) to allow for better convergence on this small dataset. The `lambda_param`
  defaults to `0.01`.
* *`model.fit(X_normalized, y)`:* The SVM model is trained using the normalised data.
* *`predictions = model.predict(X_normalized)`:* After training, the model is used to make predictions on the
  *same* normalised training data to see how well it learned to classify these known points.
* *`print("SVM Predictions:", predictions)`:* The predicted labels are printed.

*Limitations of this specific implementation:*
* *Stochastic Gradient Descent (SGD) for updates:* This code uses a basic SGD approach. While effective for
  large datasets, more advanced SVM solvers (e.g., Sequential Minimal Optimisation - SMO) are generally more
  efficient and guarantee convergence to the optimal solution for the dual problem.
* *No Kernel Trick:* This implementation only supports linear separation. It cannot handle non-linearly separable
  data without manually transforming the features.
* *Simplified Loss Function:* The update rule is a simplified interpretation of the hinge loss gradient, not a
  direct implementation of the standard dual SVM optimisation.
* *No Dual Problem:* The mathematical elegance and computational benefits of solving the SVM in its dual form
  (which naturally leads to the kernel trick and identifies support vectors) are not present here.
* *Hyperparameter Tuning:* Like all machine learning models, the performance of this SVM implementation is sensitive
  to the chosen `learning_rate`, `lambda_param`, and `n_iters`. These would typically be tuned using techniques
  like cross-validation.

