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
# Create a dataset of input pairs (x1, x2) and their expected sum
inputs = [(1, 2), (2, 3), (3, 4), (5, 5), (10, 20), (7, 8)]
target = [sum(pair) for pair in inputs]  # Expected outputs are the sums of pairs

nn = SimpleNeuralNetwork()

# Train the neural network on the dataset
nn.train(inputs, target)

# Test predictions
predictions = [nn.predict(input_vector) for input_vector in inputs]
print("Predictions:")
for input_vector, prediction in zip(inputs, predictions):
    print(f"Input: {input_vector}, Predicted Sum: {prediction:.2f}, Actual Sum: {sum(input_vector)}")

# Additional test inputs outside of the original training set
new_inputs = [(12, 13), (15, 5), (1, 10)]
new_predictions = [nn.predict(input_vector) for input_vector in new_inputs]

print("\nNew Predictions on Unseen Inputs:")
for input_vector, prediction in zip(new_inputs, new_predictions):
    print(f"Input: {input_vector}, Predicted Sum: {prediction:.2f}, Actual Sum: {sum(input_vector)}")
