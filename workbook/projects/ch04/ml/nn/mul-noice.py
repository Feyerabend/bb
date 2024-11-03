import random

class SimpleNeuralNetwork:
    def __init__(self):
        # Initialize weights and biases for a hidden layer
        self.hidden_weights = [[random.uniform(-0.1, 0.1) for _ in range(2)] for _ in range(4)]  # 4 neurons in hidden layer
        self.hidden_bias = [random.uniform(-0.1, 0.1) for _ in range(4)]
        self.output_weights = [random.uniform(-0.1, 0.1) for _ in range(4)]  # Change to match number of hidden neurons
        self.output_bias = random.uniform(-0.1, 0.1)

    def hidden_layer(self, inputs):
        # Calculate outputs for hidden layer using ReLU
        return [max(0, sum(w * i for w, i in zip(self.hidden_weights[j], inputs)) + self.hidden_bias[j]) for j in range(4)]

    def predict(self, inputs):
        hidden_output = self.hidden_layer(inputs)
        # Output layer calculation
        output = sum(w * h for w, h in zip(self.output_weights, hidden_output)) + self.output_bias
        return output

    def train(self, inputs, targets, learning_rate=0.01, epochs=20000):
        for _ in range(epochs):
            for input_vector, expected in zip(inputs, targets):
                # Forward pass
                hidden_output = self.hidden_layer(input_vector)
                output = self.predict(input_vector)
                error = expected - output

                # Update weights and biases for output layer
                for j in range(4):
                    # Gradient clipping to prevent large updates
                    update = learning_rate * error * hidden_output[j]
                    self.output_weights[j] += max(-0.1, min(0.1, update))  # Clip updates
                self.output_bias += learning_rate * error  # Could also clip here if needed

                # Update weights and biases for hidden layer
                for j in range(4):
                    for i in range(2):
                        if hidden_output[j] > 0:  # Ensure ReLU condition
                            update = learning_rate * error * self.output_weights[j] * input_vector[i]
                            self.hidden_weights[j][i] += max(-0.1, min(0.1, update))  # Clip updates
                    self.hidden_bias[j] += learning_rate * error * self.output_weights[j]

# Sample data for multiplication (normalized)
inputs = [
    [0.1, 0.3],   # 2 * 3
    [0.1, 0.4],   # 1 * 4
    [0.5, 0.2],   # 5 * 2
    [0.1, 0.05],  # 1 * 0.5
    [0.3, 0.3],   # 3 * 3
    [0.7, 0.7],   # 7 * 7
    [0.1, 1.0],   # 1 * 10
    [0.8, 0.5],   # 8 * 5
    [0.12, 0.3],  # 12 * 3
    [0.4, 0.6],   # 4 * 6
    [0.2, 0.9],   # 2 * 9
    [0.9, 0.2],   # 9 * 2
    [0.4, 0.5],   # 4 * 5
    [0.5, 0.6]    # 5 * 6
]

# Targets: products of the input pairs (normalized)
targets = [a * b for a, b in inputs]

# Initialize and train the neural network
nn = SimpleNeuralNetwork()
nn.train(inputs, targets)

# Testing the trained model with some additional examples (normalized)
test_inputs = [[0.3, 0.5], [0.6, 0.7], [0.1, 0.8], [0.9, 0.1], [0.2, 0.6], [0.4, 0.5], [0.5, 0.5]]
for test_input in test_inputs:
    prediction = nn.predict(test_input)
    actual = test_input[0] * test_input[1]
    print(f"Predicted: {prediction:.2f}, Actual: {actual:.2f}")