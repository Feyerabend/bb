import random

class Perceptron:
    def __init__(self, learning_rate=0.1, n_iters=1000):
        self.lr = learning_rate
        self.n_iters = n_iters
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        n_samples, n_features = len(X), len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0
        
        for _ in range(self.n_iters):
            for idx, x_i in enumerate(X):
                linear_output = sum(w * x for w, x in zip(self.weights, x_i)) + self.bias
                y_predicted = self._activation_function(linear_output)

                # Update weights and bias
                update = self.lr * (y[idx] - y_predicted)
                self.weights = [w + update * x for w, x in zip(self.weights, x_i)]
                self.bias += update

    def _activation_function(self, x):
        return 1 if x >= 0 else 0

    def predict(self, X):
        linear_output = [sum(w * x for w, x in zip(self.weights, x_i)) + self.bias for x_i in X]
        return [self._activation_function(x) for x in linear_output]

# Example usage
X = [[0, 0], [0, 1], [1, 0], [1, 1]]  # AND logic gate input
y = [0, 0, 0, 1]  # AND logic gate output

p = Perceptron()
p.fit(X, y)
predictions = p.predict(X)

print("Perceptron Predictions:", predictions)