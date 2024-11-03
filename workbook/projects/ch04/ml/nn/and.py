import random
import math

class SimpleNeuralNetwork:
    def __init__(self, input_size):
        self.weights = [random.random() for _ in range(input_size)]
        self.bias = random.random()
    
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
    
    def predict(self, inputs):
        linear_combination = sum(w * i for w, i in zip(self.weights, inputs)) + self.bias
        return self.sigmoid(linear_combination)

    def train(self, inputs, target, learning_rate=0.1):
        for input_vector, expected in zip(inputs, target):
            output = self.predict(input_vector)
            error = expected - output

            # Update weights and bias
            for i in range(len(self.weights)):
                self.weights[i] += learning_rate * error * output * (1 - output) * input_vector[i]

            self.bias += learning_rate * error * output * (1 - output)

# Example usage
inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]  # AND gate
target = [0, 0, 0, 1]

nn = SimpleNeuralNetwork(input_size=2)

# Training
for _ in range(1000):
    nn.train(inputs, target)

# Predictions
predictions = [nn.predict(input_vector) for input_vector in inputs]
print("Predictions:", [round(p) for p in predictions])
