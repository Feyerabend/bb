import numpy as np

class DecisionTree:
    """ A very simple decision tree regressor. """
    def __init__(self, max_depth=1):
        self.max_depth = max_depth
        self.tree = None

    def fit(self, X, y):
        self.tree = self._build_tree(X, y)

    def _build_tree(self, X, y, depth=0):
        # If all the target values are the same, return that value
        if len(set(y)) == 1 or depth >= self.max_depth:
            return np.mean(y)

        # Find the best split
        n_samples, n_features = X.shape
        best_feature, best_value = self._best_split(X, y)
        
        if best_feature is None:
            return np.mean(y)

        # Split the data
        left_indices = X[:, best_feature] < best_value
        right_indices = X[:, best_feature] >= best_value
        left_tree = self._build_tree(X[left_indices], y[left_indices], depth + 1)
        right_tree = self._build_tree(X[right_indices], y[right_indices], depth + 1)

        return (best_feature, best_value, left_tree, right_tree)

    def _best_split(self, X, y):
        n_samples, n_features = X.shape
        best_mse = float('inf')
        best_feature, best_value = None, None
        
        for feature in range(n_features):
            values = np.unique(X[:, feature])
            for value in values:
                left_indices = X[:, feature] < value
                right_indices = X[:, feature] >= value
                if len(y[left_indices]) == 0 or len(y[right_indices]) == 0:
                    continue
                
                mse = self._calculate_mse(y, left_indices, right_indices)
                if mse < best_mse:
                    best_mse = mse
                    best_feature = feature
                    best_value = value

        return best_feature, best_value

    def _calculate_mse(self, y, left_indices, right_indices):
        left_mean = np.mean(y[left_indices]) if len(y[left_indices]) > 0 else 0
        right_mean = np.mean(y[right_indices]) if len(y[right_indices]) > 0 else 0
        mse = np.mean((y[left_indices] - left_mean) ** 2) + np.mean((y[right_indices] - right_mean) ** 2)
        return mse

    def predict(self, X):
        return np.array([self._predict_single(sample, self.tree) for sample in X])

    def _predict_single(self, sample, tree):
        if isinstance(tree, tuple):
            feature, value, left_tree, right_tree = tree
            if sample[feature] < value:
                return self._predict_single(sample, left_tree)
            else:
                return self._predict_single(sample, right_tree)
        else:
            return tree

class GradientBoostingRegressor:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=1):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.trees = []

    def fit(self, X, y):
        # Initial prediction
        y_pred = np.full(y.shape, np.mean(y))
        self.trees = []

        for _ in range(self.n_estimators):
            residuals = y - y_pred
            tree = DecisionTree(max_depth=self.max_depth)
            tree.fit(X, residuals)
            self.trees.append(tree)

            # Update predictions
            y_pred += self.learning_rate * tree.predict(X)

    def predict(self, X):
        y_pred = np.full(X.shape[0], np.mean(y))
        for tree in self.trees:
            y_pred += self.learning_rate * tree.predict(X)
        return y_pred

# Example usage
if __name__ == "__main__":
    # Sample data
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.array([1.5, 1.75, 2.25, 2.5])

    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=2)
    model.fit(X, y)

    # Predicting
    predictions = model.predict(X)
    print("Predictions:", predictions)
