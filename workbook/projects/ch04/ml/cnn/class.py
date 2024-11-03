import numpy as np
from PIL import Image
import os

class SimpleCNN:
    def __init__(self, img_size=40):
        self.img_size = img_size
        self.filter = np.array([[1, -1], [-1, 1]])  # Simple edge detection filter
        self.weights = np.random.rand(3, (img_size // 2) * (img_size // 2)) * 0.01  # For 3 classes
        self.biases = np.zeros(3)

    def convolve(self, img, conv_filter):
        output_dim = img.shape[0] - conv_filter.shape[0] + 1
        output = np.zeros((output_dim, output_dim))

        for i in range(output_dim):
            for j in range(output_dim):
                region = img[i:i+conv_filter.shape[0], j:j+conv_filter.shape[1]]
                output[i, j] = np.sum(region * conv_filter)
        return output

    def relu(self, matrix):
        return np.maximum(0, matrix)

    def max_pool(self, matrix, size=2, stride=2):
        output_dim = matrix.shape[0] // size
        pooled = np.zeros((output_dim, output_dim))

        for i in range(0, matrix.shape[0], stride):
            for j in range(0, matrix.shape[1], stride):
                pooled[i // size, j // size] = np.max(matrix[i:i + size, j:j + size])
        return pooled

    def flatten(self, matrix):
        return matrix.flatten()

    def forward(self, img):
        # Convolution step
        conv_output = self.convolve(img, self.filter)
        # Apply ReLU
        relu_output = self.relu(conv_output)
        # Max Pooling
        pooled_output = self.max_pool(relu_output)
        # Flatten for fully connected layer
        flat_output = self.flatten(pooled_output)
        # Fully Connected Layer
        scores = np.dot(self.weights, flat_output) + self.biases
        return np.argmax(scores)  # Class prediction (0: horizontal, 1: vertical, 2: diagonal)

    def load_and_preprocess_image(self, image_path):
        img = Image.open(image_path).convert('L').resize((self.img_size, self.img_size))
        img_array = np.array(img) / 255.0  # Normalize
        return img_array

    def predict(self, image_path):
        img_array = self.load_and_preprocess_image(image_path)
        prediction = self.forward(img_array)
        line_types = ['horizontal', 'vertical', 'diagonal']
        print(f"Predicted Line Type: {line_types[prediction]}")
        return line_types[prediction]

# Usage
# Assuming images are saved in 'test_images/' directory
cnn_model = SimpleCNN(img_size=40)

# Test prediction on a sample image
test_image_path = 'test_images/horizontal_variation_1.png'
predicted_line_type = cnn_model.predict(test_image_path)
print(f"Predicted class for test image: {predicted_line_type}")