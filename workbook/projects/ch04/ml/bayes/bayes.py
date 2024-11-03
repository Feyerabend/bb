class NaiveBayes:
    def __init__(self):
        self.classes = {}
        self.feature_counts = {}
    
    def fit(self, X, y):
        self.classes = {c: 0 for c in set(y)}
        self.feature_counts = {c: [] for c in set(y)}

        # Count occurrences of each class
        for label in y:
            self.classes[label] += 1

        # Count features per class
        for i in range(len(y)):
            self.feature_counts[y[i]].append(X[i][0])  # X[i][0] since X is 2D

    def predict(self, x):
        probabilities = {}
        total_count = sum(self.classes.values())

        for c in self.classes.keys():
            prior = self.classes[c] / total_count
            likelihood = 1.0

            # Calculate likelihood of the features for class c
            for feature in x:
                # Naive assumption: features are independent
                count = sum(1 for f in self.feature_counts[c] if f == feature)
                likelihood *= (count + 1) / (len(self.feature_counts[c]) + 2)  # Laplace smoothing

            probabilities[c] = prior * likelihood

        return max(probabilities, key=probabilities.get)


    def predict_with_probabilities(self, x):
        probabilities = {}
        total_count = sum(self.classes.values())

        for c in self.classes.keys():
            prior = self.classes[c] / total_count
            likelihood = 1.0

            for feature in x:
                count = sum(1 for f in self.feature_counts[c] if f == feature)
                likelihood *= (count + 1) / (len(self.feature_counts[c]) + 2)  # Laplace smoothing

            probabilities[c] = prior * likelihood

        predicted_class = max(probabilities, key=probabilities.get)
        return predicted_class, probabilities


# Simulated temperature data (e.g., in Celsius)
X = [
    [15], [18], [20], [21], [22], [25], 
    [26], [27], [28], [29], [30], [31], 
    [32], [33], [34], [35]  # More diverse temperatures
]  
y = [
    0, 0, 0, 0, 0, 0,  # Normal
    0, 0, 0, 1, 1, 1,  # Warning
    1, 1, 1, 1  # Warning
]  # Updated labels

# Create and fit the model
model = NaiveBayes()
model.fit(X, y)

# Predicting new temperature readings
# New temperature readings to predict
new_readings = [
    [21],  # Expected: Normal
    [29],  # Expected: Warning
    [33],  # Expected: Warning
    [18],  # Expected: Normal
    [15],  # Expected: Normal
    [36]   # Out of training range
]
predictions = [model.predict(reading) for reading in new_readings]

# Usage
for reading in new_readings:
    predicted_class, probs = model.predict_with_probabilities(reading)
    print(f"Prediction for temperature {reading[0]}°C: {'Warning' if predicted_class == 1 else 'Normal'}, Probabilities: {probs}")


