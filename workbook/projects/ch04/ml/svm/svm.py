import random
import numpy as np

# Function to normalize the dataset
def normalize(X):
    X = np.array(X)
    return (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0))

class SVM:
    def __init__(self, learning_rate=0.01, lambda_param=0.01, n_iters=1000):
        self.lr = learning_rate
        self.lambda_param = lambda_param
        self.n_iters = n_iters
        self.w = None
        self.b = None

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

    def _predict(self, x):
        return np.dot(x, self.w) + self.b

    def predict(self, X):
        return [1 if self._predict(x) >= 0 else -1 for x in X]

# Sample data points with clearer separation
X = [[3.1, 2.5], [1.5, 2.2], [2.3, 3.3], [5.1, 1.6], [4.0, 2.0], [0.5, 0.8]]
y = [1, 1, -1, -1, 1, -1]  # Added more points for better classification

# Normalize the feature matrix
X_normalized = normalize(X)

model = SVM(learning_rate=0.01, n_iters=20000)  # Increased iterations
model.fit(X_normalized, y)
predictions = model.predict(X_normalized)

print("SVM Predictions:", predictions)