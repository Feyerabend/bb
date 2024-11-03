from PIL import Image
import numpy as np

# 2x2 convolutional filter
filter = [
    [1, -1],
    [-1, 1]
]

# Function to apply convolution
def convolution(input_image):
    filter_size = len(filter)
    output_size = (input_image.shape[0] - filter_size + 1, input_image.shape[1] - filter_size + 1)
    output = np.zeros(output_size, dtype=np.float32)  # Use float to avoid overflow
    
    for i in range(output_size[0]):
        for j in range(output_size[1]):
            output[i][j] = (input_image[i][j] * filter[0][0] +
                            input_image[i][j + 1] * filter[0][1] +
                            input_image[i + 1][j] * filter[1][0] +
                            input_image[i + 1][j + 1] * filter[1][1])
    return output

# Function to apply ReLU activation
def relu(input_matrix):
    return np.maximum(0, input_matrix)

# Function for max pooling
def max_pooling(input_matrix):
    output = []
    for i in range(0, len(input_matrix), 2):
        row = []
        for j in range(0, len(input_matrix[i]), 2):
            # Ensure we're within bounds for pooling
            if i + 1 < len(input_matrix) and j + 1 < len(input_matrix[i]):
                max_value = max(input_matrix[i][j], 
                                 input_matrix[i][j + 1],
                                 input_matrix[i + 1][j], 
                                 input_matrix[i + 1][j + 1])
                row.append(max_value)
        if row:  # Only append rows that have values
            output.append(row)
    return np.array(output)

# CNN forward pass that processes an image
def cnn_forward(input_image):
    # Convert the image to grayscale and then to a numpy array
    input_array = np.array(input_image.convert("L"), dtype=np.float32)  # Convert to grayscale and use float
    print("Input Image Size:", input_array.shape)

    # Step 1: Convolution
    conv_output = convolution(input_array)
    print("Convolution Output Size:", conv_output.shape)

    # Step 2: ReLU Activation
    relu_output = relu(conv_output)
    print("ReLU Output Size:", relu_output.shape)

    # Step 3: Max Pooling
    pooled_output = max_pooling(relu_output)
    print("Max Pooling Output Size:", pooled_output.shape)

    return pooled_output

# Function to visualize output
def visualize_output(output_array):
    # Normalize output for visualization
    output_array = np.clip(output_array, 0, None)  # Clip negative values to 0
    # Scale to 0-255 for image display
    output_array = (output_array - np.min(output_array)) / (np.max(output_array) - np.min(output_array)) * 255
    output_image = Image.fromarray(output_array.astype(np.uint8))
    return output_image

# Main execution
if __name__ == "__main__":
    # Load an image using Pillow
    input_image = Image.open("input_image.jpg")  # Change to your image path
    output_array = cnn_forward(input_image)
    
    # Visualize and save the output image
    output_image = visualize_output(output_array)
    output_image.save("output_image.jpg")  # Save the processed image
    output_image.show()  # Show the processed image