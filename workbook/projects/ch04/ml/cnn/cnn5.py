# Simple CNN Implementation in MicroPython with a 3x3 Filter

# Example 5x5 grayscale image
input_image = [
    [1, 2, 0, 1, 2],
    [3, 1, 1, 0, 1],
    [0, 2, 3, 1, 0],
    [1, 0, 2, 3, 1],
    [2, 1, 0, 2, 3]
]

# 3x3 convolutional filter
filter = [
    [1, -1, 0],
    [-1, 1, 1],
    [0, 1, -1]
]

# Function to apply convolution
def convolution(input_image, filter):
    output_size = len(input_image) - len(filter) + 1
    output = [[0] * output_size for _ in range(output_size)]
    
    for i in range(output_size):
        for j in range(output_size):
            output[i][j] = (input_image[i][j] * filter[0][0] +
                            input_image[i][j + 1] * filter[0][1] +
                            input_image[i][j + 2] * filter[0][2] +
                            input_image[i + 1][j] * filter[1][0] +
                            input_image[i + 1][j + 1] * filter[1][1] +
                            input_image[i + 1][j + 2] * filter[1][2] +
                            input_image[i + 2][j] * filter[2][0] +
                            input_image[i + 2][j + 1] * filter[2][1] +
                            input_image[i + 2][j + 2] * filter[2][2])
    return output

# Function to apply ReLU activation
def relu(input_matrix):
    return [[max(0, value) for value in row] for row in input_matrix]

# Function for max pooling
def max_pooling(input_matrix):
    output = []
    for i in range(0, len(input_matrix), 2):
        row = []
        for j in range(0, len(input_matrix[i]), 2):
            max_value = max(input_matrix[i][j], input_matrix[i][j + 1],
                             input_matrix[i + 1][j], input_matrix[i + 1][j + 1])
            row.append(max_value)
        output.append(row)
    return output

# Fully connected layer with simple classification
def fully_connected(input_matrix):
    # Assume we have a simple threshold for binary classification
    flattened = [item for sublist in input_matrix for item in sublist]
    total = sum(flattened)
    return 1 if total > 0 else 0  # Classify based on summed values

# CNN forward pass
def cnn_forward(input_image):
    conv_output = convolution(input_image, filter)
    relu_output = relu(conv_output)
    pooled_output = max_pooling(relu_output)
    prediction = fully_connected(pooled_output)
    return prediction

# Run the CNN
prediction = cnn_forward(input_image)
print("Predicted class:", prediction)
