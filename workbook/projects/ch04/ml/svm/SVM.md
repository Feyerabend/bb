## SVM

Support Vector Machines (SVM) are a supervised learning algorithm used primarily for classification, but also for regression tasks. SVMs work by finding the optimal hyperplane that best separates data points of different classes in a high-dimensional space. This hyperplane acts as a decision boundary, maximizing the margin between classes, which helps in achieving good generalization on new, unseen data.

The key idea in SVM is to find the hyperplane with the maximum margin. The margin is the distance between the closest data points (support vectors) from each class and the hyperplane. By maximizing this margin, SVM aims to reduce the chance of misclassification and improve the model's robustness. Mathematically, this can be formulated as a constrained optimization problem, typically solved using Lagrange multipliers.

Linear vs. Non-linear SVM

For linearly separable data, a linear SVM finds a straight hyperplane that divides the classes. However, real-world data is often not linearly separable. In such cases, SVMs can employ a technique called the kernel trick, which maps the data into a higher-dimensional space where a linear separation is possible. Common kernel functions include:
- Linear kernel: Best for linearly separable data.
- Polynomial kernel: Useful for data that can be separated by polynomial boundaries.
- Radial Basis Function (RBF) kernel (Gaussian kernel): Useful for complex data structures with no linear separability.
- Sigmoid kernel: Sometimes used in neural network applications.

The kernel trick allows SVM to handle complex datasets without explicitly transforming the data to higher dimensions, making it computationally efficient.



### SVM Objective Function in LaTeX

Given a dataset of points $\((x_i, y_i)\) where \(x_i\)$ represents the feature vectors
and $\(y_i \in \{-1, 1\}\)$ the class labels, the optimization problem SVM solves is:

$$\[
\min_{w, b, \xi} \frac{1}{2} ||w||^2 + C \sum_{i=1}^n \xi_i
\]$$

subject to:

$$\[
y_i (w \cdot x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0, \quad \forall i
\]$$

where:
- $\( w \)$ is the weight vector that defines the orientation of the hyperplane,
- $\( b \)$ is the bias term (or intercept),
- $\( \xi_i \)$ are slack variables that allow some misclassification in cases where data isn't linearly separable,
- $\( C \)$ is the regularization parameter, balancing the trade-off between maximizing the margin and minimizing classification errors.

### Kernel Trick

In cases where data is not linearly separable, SVM can project data into a higher-dimensional space using a **kernel function** $\( K(x_i, x_j) \)$, which implicitly computes the dot product in this transformed space. Common kernels include:
1. **Linear kernel**: $\( K(x_i, x_j) = x_i \cdot x_j \)$
2. **Polynomial kernel**: $\( K(x_i, x_j) = (x_i \cdot x_j + 1)^d \)$, where $\(d\)$ is the degree.
3. **Radial Basis Function (RBF)**: $\( K(x_i, x_j) = \exp\left(-\gamma ||x_i - x_j||^2\right) \)$, where $\(\gamma\)$ is a parameter defining the spread of the kernel.

### Prediction

For a new data point $\( x \)$, the SVM model predicts the label based on the sign of:

$$\[
f(x) = \text{sign}(w \cdot x + b)
\]$$

If $\( f(x) > 0 \)$, the point is classified as $\(+1\); if \( f(x) < 0 \)$, it is classified as $\(-1\)$.

Strengths and Limitations

SVMs are highly effective in high-dimensional spaces and with a clear margin of separation. They work well with small to medium datasets and offer flexibility through kernel functions. However, SVMs can be computationally intensive with large datasets and may perform less effectively when classes overlap significantly, making them sensitive to the choice of the kernel and parameters.

Overall, SVM remains a powerful, mathematically robust tool in machine learning, particularly in applications such as text classification, image recognition, and bioinformatics.
