input_image = [
    [1, 2, 0, 1],
    [3, 1, 1, 0],
    [0, 2, 3, 1],
    [1, 0, 2, 3]
]

# 2x2 convolutional filter
filter = [
    [1, -1],
    [-1, 1]
]

# Function to apply convolution
def convolution(input_image, filter):
    output_size = len(input_image) - len(filter) + 1
    output = [[0] * output_size for _ in range(output_size)]
    
    for i in range(output_size):
        for j in range(output_size):
            output[i][j] = (input_image[i][j] * filter[0][0] +
                            input_image[i][j + 1] * filter[0][1] +
                            input_image[i + 1][j] * filter[1][0] +
                            input_image[i + 1][j + 1] * filter[1][1])
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
            # Check to prevent index out of range errors
            if i + 1 < len(input_matrix) and j + 1 < len(input_matrix[i]):
                max_value = max(input_matrix[i][j], 
                                 input_matrix[i][j + 1],
                                 input_matrix[i + 1][j], 
                                 input_matrix[i + 1][j + 1])
                row.append(max_value)
        if row:  # Only append non-empty rows
            output.append(row)
    return output

# Fully connected layer with simple classification
def fully_connected(input_matrix):
    flattened = [item for sublist in input_matrix for item in sublist]
    total = sum(flattened)
    return 1 if total > 0 else 0  # Classify based on summed values

# CNN forward pass
def cnn_forward(input_image):
    print("Input Image:")
    for row in input_image:
        print(row)

    # Step 1: Convolution
    conv_output = convolution(input_image, filter)
    print("\nConvolution Output:")
    for row in conv_output:
        print(row)

    # Step 2: ReLU Activation
    relu_output = relu(conv_output)
    print("\nReLU Output:")
    for row in relu_output:
        print(row)

    # Step 3: Max Pooling
    pooled_output = max_pooling(relu_output)
    print("\nMax Pooling Output:")
    for row in pooled_output:
        print(row)

    # Step 4: Fully Connected Layer
    prediction = fully_connected(pooled_output)
    print("\nPredicted class:", prediction)
    
    return prediction

# Run the CNN
cnn_forward(input_image)