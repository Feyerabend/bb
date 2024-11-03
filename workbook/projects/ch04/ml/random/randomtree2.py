import random

class DecisionTree:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.tree = None

    def fit(self, X, y):
        self.tree = self._build_tree(X, y)

    def _build_tree(self, X, y, depth=0):
        if len(set(y)) == 1 or (self.max_depth and depth == self.max_depth):
            return max(set(y), key=list(y).count)

        # Find the best split
        best_gain = 0
        best_criteria = None
        best_sets = None

        for feature_index in range(len(X[0])):
            values = set(x[feature_index] for x in X)
            for value in values:
                left_indices = [i for i, x in enumerate(X) if x[feature_index] < value]
                right_indices = [i for i, x in enumerate(X) if x[feature_index] >= value]
                if left_indices and right_indices:
                    gain = self._information_gain(y, left_indices, right_indices)
                    if gain > best_gain:
                        best_gain = gain
                        best_criteria = (feature_index, value)
                        best_sets = (left_indices, right_indices)

        if best_gain == 0:
            return max(set(y), key=list(y).count)

        left_tree = self._build_tree([X[i] for i in best_sets[0]], [y[i] for i in best_sets[0]], depth + 1)
        right_tree = self._build_tree([X[i] for i in best_sets[1]], [y[i] for i in best_sets[1]], depth + 1)
        return (best_criteria, left_tree, right_tree)

    def _information_gain(self, y, left_indices, right_indices):
        def entropy(labels):
            from math import log2
            total = len(labels)
            counts = {label: labels.count(label) for label in set(labels)}
            return -sum((count / total) * log2(count / total) for count in counts.values())

        total_entropy = entropy(y)
        left_entropy = entropy([y[i] for i in left_indices])
        right_entropy = entropy([y[i] for i in right_indices])
        p_left = len(left_indices) / len(y)
        p_right = len(right_indices) / len(y)
        return total_entropy - (p_left * left_entropy + p_right * right_entropy)

    def predict(self, X):
        return [self._predict_tree(x, self.tree) for x in X]

    def _predict_tree(self, x, tree):
        if not isinstance(tree, tuple):
            return tree
        feature_index, value = tree[0]
        if x[feature_index] < value:
            return self._predict_tree(x, tree[1])
        else:
            return self._predict_tree(x, tree[2])

class RandomForest:
    def __init__(self, n_trees=10, max_depth=None):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.trees = []

    def fit(self, X, y):
        for _ in range(self.n_trees):
            # Bootstrap sampling
            indices = [random.randint(0, len(X) - 1) for _ in range(len(X))]
            sample_X = [X[i] for i in indices]
            sample_y = [y[i] for i in indices]
            tree = DecisionTree(self.max_depth)
            tree.fit(sample_X, sample_y)
            self.trees.append(tree)

    def predict(self, X):
        predictions = [tree.predict(X) for tree in self.trees]
        # Majority vote
        return [max(set(pred), key=list(pred).count) for pred in zip(*predictions)]




# Example usage
import numpy as np

def generate_data(num_points=100):
    X = []
    y = []

    for _ in range(num_points):
        # Generate random coordinates
        x1 = np.random.uniform(0, 6)  # Range can be adjusted
        x2 = np.random.uniform(0, 4)
        X.append([x1, x2])

        # Simple decision boundary: y = -0.5 * x + 3
        if x1 + x2 > 5:  # Adjusting the condition to mimic your example's classification
            y.append(1)  # Class 1
        else:
            y.append(-1)  # Class -1

    return np.array(X), np.array(y)

# Example usage:
num_samples = 2000  # Number of samples to generate
X, y = generate_data(num_samples)

# Print the generated data
print("Generated Data Points (X):")
print(X)
print("\nLabels (y):")
print(y)

rf = RandomForest(n_trees=5, max_depth=2)
rf.fit(X, y)
predictions = rf.predict(X)

print("Random Forest Predictions:", predictions)

from PIL import Image, ImageDraw

def create_image_with_predictions(predictions):
    # Create a blank image
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)

    # Draw predictions
    for idx, prediction in enumerate(predictions):
        color = 'green' if prediction == 1 else 'red'  # Color based on prediction
        draw.rectangle([20 + idx * 40, 40, 60 + idx * 40, 80], fill=color)

    img.show()

# Example usage
predictions = [1, 1, -1, -1]
create_image_with_predictions(predictions)





