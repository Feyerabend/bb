from PIL import Image
import numpy as np

# Original 4x4 grayscale image
image1 = np.array([
    [1, 2, 0, 1],
    [3, 1, 1, 0],
    [0, 2, 3, 1],
    [1, 0, 2, 3]
]) * 85  # Normalize to 0-255

# Original 5x5 grayscale image
image2 = np.array([
    [1, 2, 0, 1, 2],
    [3, 1, 1, 0, 1],
    [0, 2, 3, 1, 0],
    [1, 0, 2, 3, 1],
    [2, 1, 0, 2, 3]
]) * 85  # Normalize to 0-255

# Function to create an enlarged image
def create_enlarged_image(data, pixel_size):
    # Create an enlarged array
    enlarged_image = np.kron(data, np.ones((pixel_size, pixel_size)))
    return Image.fromarray(enlarged_image.astype('uint8'), 'L')

# Create enlarged images
enlarged_image1 = create_enlarged_image(image1, pixel_size=10)
enlarged_image2 = create_enlarged_image(image2, pixel_size=10)

# Save the images as PNG
enlarged_image1.save('grayscale_image_4x4.png')
enlarged_image2.save('grayscale_image_5x5.png')

print("Images saved as 'grayscale_image_4x4.png' and 'grayscale_image_5x5.png'")
