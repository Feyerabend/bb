
class DecisionTree:
    def __init__(self, depth=1):
        self.depth = depth
        self.left = None
        self.right = None
        self.value = None
        self.feature_index = None

    def fit(self, X, y):
        # Base case: If all labels are the same, create a leaf node
        if len(set(y)) == 1:
            self.value = y[0]
            return
        
        # Stop splitting if max depth reached
        if self.depth == 0:
            self.value = max(set(y), key=list(y).count)  # Majority vote
            return
        
        # Find the best split
        best_gain = 0
        best_feature = None
        best_left_indices = None
        best_right_indices = None

        for feature_index in range(len(X[0])):
            # Define the threshold for splitting, here we use 0.5
            left_indices = [i for i in range(len(X)) if X[i][feature_index] < 0.5]
            right_indices = [i for i in range(len(X)) if X[i][feature_index] >= 0.5]

            # Calculate information gain
            gain = self.information_gain(y, left_indices, right_indices)

            if gain > best_gain:
                best_gain = gain
                best_feature = feature_index
                best_left_indices = left_indices
                best_right_indices = right_indices

        # Split the dataset and create left and right child nodes
        if best_gain > 0:
            self.feature_index = best_feature  # Store the feature index for prediction
            self.left = DecisionTree(depth=self.depth - 1)
            self.right = DecisionTree(depth=self.depth - 1)
            self.left.fit([X[i] for i in best_left_indices], [y[i] for i in best_left_indices])
            self.right.fit([X[i] for i in best_right_indices], [y[i] for i in best_right_indices])
        else:
            self.value = max(set(y), key=list(y).count)

    def information_gain(self, y, left_indices, right_indices):
        p = len(left_indices) / len(y) if len(y) > 0 else 0
        return self.entropy(y) - (p * self.entropy([y[i] for i in left_indices]) +
                                   (1 - p) * self.entropy([y[i] for i in right_indices]))

    def entropy(self, y):
        total = len(y)
        if total == 0:
            return 0  # Avoid division by zero
        counts = self.count_occurrences(y)
        entropy_value = 0
        for count in counts.values():
            if count > 0:  # Avoid log(0)
                probability = count / total
                entropy_value -= probability * self.log2(probability)
        return entropy_value

    def count_occurrences(self, y):
        counts = {}
        for item in y:
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1
        return counts

    def log2(self, x):
        if x <= 0:
            raise ValueError("Logarithm is undefined for non-positive values.")

        count = 0
        while x >= 2:
            x /= 2
            count += 1

        # Now x is between 1 and 2, we will find the fractional part
        # This can be done by using a loop for a certain precision
        fractional_part = 0.0
        precision = 10  # Set the number of decimal places for precision
        for i in range(precision):
            x *= 2
            if x >= 2:
                fractional_part += 1 / (2 ** (i + 1))
                x -= 2

        return count + fractional_part


    def predict(self, x):
        if self.value is not None:
            return self.value
        if x[self.feature_index] < 0.5:
            return self.left.predict(x)
        else:
            return self.right.predict(x)

# Example usage
X = [[0.1], [0.4], [0.6], [0.9]]  # Features: e.g., temperature
y = [0, 0, 1, 1]  # Labels: 0 or 1

tree = DecisionTree(depth=2)
tree.fit(X, y)

# Predicting new samples
predictions = [tree.predict([0.3]), tree.predict([0.8])]
print("Predictions for inputs [0.3] and [0.8]:", predictions)

predictions = [tree.predict([0.123]), tree.predict([0.76543])]
print("Predictions for inputs [0.123] and [0.76543]:", predictions)
