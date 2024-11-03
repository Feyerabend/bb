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
X = [[3.1, 2.5], [1.5, 2.2], [2.3, 3.3], [5.1, 1.6]]  # Sample data points
y = [1, 1, -1, -1]  # Labels

rf = RandomForest(n_trees=5, max_depth=2)
rf.fit(X, y)
predictions = rf.predict(X)

print("Random Forest Predictions:", predictions)
