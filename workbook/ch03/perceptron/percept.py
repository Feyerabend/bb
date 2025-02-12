import os
import random

class Perceptron:

    def __init__(self, input_size):
        # init weights and bias to random values between -1 and 1
        self.weights = [random.uniform(-1, 1) for _ in range(input_size)]
        self.bias = random.uniform(-1, 1)
        self.learning_rate = 0.1

    def activation(self, x):
        # step function (for binary classification)
        return 1 if x >= 0 else 0

    def predict(self, inputs):
        # weighted sum of inputs + bias
        summation = sum([w * i for w, i in zip(self.weights, inputs)]) + self.bias
        return self.activation(summation)
    
    def train(self, training_data, labels, epochs):
        # train the perceptron using the Perceptron learning rule
        for _ in range(epochs):
            for inputs, label in zip(training_data, labels):
                prediction = self.predict(inputs)
                error = label - prediction
                # update weights and bias
                for i in range(len(self.weights)):
                    self.weights[i] += self.learning_rate * error * inputs[i]
                self.bias += self.learning_rate * error

# load images from a directory and assign labels
def load_images_from_directory(directory, label):
    images = []
    labels = []
    for filename in os.listdir(directory):
        if filename.endswith(".ppm"):
            # read image data from PPM file
            with open(os.path.join(directory, filename), 'r') as f:
                lines = f.readlines()
                pixels = []
                for line in lines[3:]:  # skip header
                    pixels += [int(val) for val in line.split()]
                images.append(pixels)
                labels.append(label)
    return images, labels

# load all training and test data
def load_all_data():
    train_images = []
    train_labels = []
    test_images = []
    test_labels = []

    # load training data
    for shape, label in zip(["circle", "square", "line"], [0, 1, 2]):
        shape_images, shape_labels = load_images_from_directory(f"train/{shape}", label)
        train_images += shape_images
        train_labels += shape_labels

    # load test data
    for shape, label in zip(["circle", "square", "line"], [0, 1, 2]):
        shape_images, shape_labels = load_images_from_directory(f"test/{shape}", label)
        test_images += shape_images
        test_labels += shape_labels

    return train_images, train_labels, test_images, test_labels

# init perceptron
input_size = 64  # 8x8 image (flattened to 64)
perceptron = Perceptron(input_size)

# load training and testing data
train_data, train_labels, test_data, test_labels = load_all_data()

# train perceptron
perceptron.train(train_data, train_labels, epochs=10)

# evaluate perceptron on the test data
correct_predictions = 0
total_predictions = len(test_labels)
confusion_matrix = {0: {0: 0, 1: 0, 2: 0}, 1: {0: 0, 1: 0, 2: 0}, 2: {0: 0, 1: 0, 2: 0}}

for inputs, label in zip(test_data, test_labels):
    prediction = perceptron.predict(inputs)
    if prediction == label:
        correct_predictions += 1
    confusion_matrix[label][prediction] += 1

accuracy = correct_predictions / total_predictions * 100
print(f"Accuracy: {accuracy:.2f}%")

print("Confusion Matrix:")
for actual in range(3):
    print(f"Actual {actual}: {confusion_matrix[actual]}")
