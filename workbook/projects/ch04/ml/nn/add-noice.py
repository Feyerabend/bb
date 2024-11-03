import random

class SimpleNeuralNetwork:
    def __init__(self):
        # Initialize weights and bias for two inputs
        self.weights = [random.random(), random.random()]  # Two weights for two inputs
        self.bias = random.random()  # One bias term
    
    def predict(self, inputs):
        # Linear combination of inputs and weights + bias
        linear_combination = sum(w * i for w, i in zip(self.weights, inputs)) + self.bias
        return linear_combination  # Return unbounded output for addition task

    def train(self, inputs, target, learning_rate=0.01, epochs=10000):
        for _ in range(epochs):
            for input_vector, expected in zip(inputs, target):
                output = self.predict(input_vector)
                error = expected - output

                # Update weights and bias
                for i in range(len(self.weights)):
                    self.weights[i] += learning_rate * error * input_vector[i]

                self.bias += learning_rate * error

# Example usage
# Create a dataset of input pairs (x1, x2) and their expected sum with some noise
inputs = [(1, 2), (2, 3), (3, 4), (5, 5), (10, 20), (7, 8)]
target = [
    3.5,  # Introduced noise (actual sum is 3)
    5.0,  # Exact match
    7.0,  # Exact match
    11.0,  # Introduced noise (actual sum is 10)
    30.0,  # Exact match
    15.5   # Introduced noise (actual sum is 15)
]

nn = SimpleNeuralNetwork()

# Train the neural network on the dataset
nn.train(inputs, target)

# Test predictions
predictions = [nn.predict(input_vector) for input_vector in inputs]
print("Predictions:")
for input_vector, prediction in zip(inputs, predictions):
    print(f"Input: {input_vector}, Predicted Sum: {prediction:.2f}, Actual Sum: {sum(input_vector)}")