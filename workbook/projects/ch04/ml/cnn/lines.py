import random
import numpy as np
from PIL import Image

# Function to generate variations of a line with reduced noise
def generate_variations(line, num_variations, noise_probability=0.2):
    variations = []
    for _ in range(num_variations):
        variation = [row[:] for row in line]
        for i in range(len(variation)):
            for j in range(len(variation[i])):
                if random.random() < noise_probability:  # Adjusted noise probability to 10%
                    variation[i][j] = 1 - variation[i][j]
        variations.append(variation)
    return variations

# Example line representations (0: background, 1: line)
horizontal_line = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

vertical_line = [
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
]

diagonal_line = [
    [1 if i == j else 0 for j in range(10)] for i in range(10)
]

# Generate variations for each line type with reduced noise
line_variations = {
    "horizontal": generate_variations(horizontal_line, 5, noise_probability=0.1),
    "vertical": generate_variations(vertical_line, 5, noise_probability=0.1),
    "diagonal": generate_variations(diagonal_line, 5, noise_probability=0.1)
}

# Simple CNN model
class SimpleCNN:
    def __init__(self):
        # Weights for each line type (for simplicity, hardcoded for this example)
        self.weights = np.array([[1, -1], [-1, 1]])

    def convolution(self, input_image):
        output_size = len(input_image) - 1
        output = [[0] * output_size for _ in range(output_size)]
        
        for i in range(output_size):
            for j in range(output_size):
                output[i][j] = (
                    input_image[i][j] * self.weights[0][0] +
                    input_image[i][j + 1] * self.weights[0][1] +
                    input_image[i + 1][j] * self.weights[1][0] +
                    input_image[i + 1][j + 1] * self.weights[1][1]
                )
        return output

    def relu(self, input_matrix):
        return [[max(0, value) for value in row] for row in input_matrix]

    def max_pooling(self, input_matrix):
        output = []
        for i in range(0, len(input_matrix), 2):
            if i + 1 >= len(input_matrix):
                break
            
            row = []
            for j in range(0, len(input_matrix[i]), 2):
                if j + 1 >= len(input_matrix[i]):
                    break
                    
                max_value = max(input_matrix[i][j], input_matrix[i][j + 1],
                                 input_matrix[i + 1][j], input_matrix[i + 1][j + 1])
                row.append(max_value)
            output.append(row)
        return output

    def predict(self, input_image):
        conv_output = self.convolution(input_image)
        relu_output = self.relu(conv_output)
        pooled_output = self.max_pooling(relu_output)

        # Simple classifier based on total
        total = sum(sum(row) for row in pooled_output)
        if total > 5:  # Adjust threshold for simplicity
            return 1
        else:
            return 0

# Create images for original lines and variations
def create_line_images():
    for line_type, variations in line_variations.items():
        for idx, variation in enumerate(variations):
            img = Image.new('1', (10, 10))  # 10x10 image for clarity
            img.putdata([pixel for row in variation for pixel in row])
            img.save(f'{line_type}_variation_{idx + 1}.png')

# Create original line images
create_line_images()

# Test variations
print("Testing predictions on variations:")
for line_type, variations in line_variations.items():
    for idx, variation in enumerate(variations):
        predicted_class = SimpleCNN().predict(variation)
        actual_class = 1  # Assuming all variations should be classified as lines
        print(f"{line_type.capitalize()} Variation {idx + 1}: Predicted class: {predicted_class}, Actual class: {actual_class}")

        # Convert the binary line representation to an image and save it
        img = Image.new('1', (10, 10))  # Larger size for better visibility
        img.putdata([pixel for row in variation for pixel in row])
        img.save(f'{line_type}_variation_{idx + 1}.png')