import os
import random

# create binary image with a circle
def generate_circle_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    cx, cy = size // 2, size // 2  # circle center
    radius = size // 3
    for x in range(size):
        for y in range(size):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                image[x][y] = 1  # set pixel to white (circle)
    return image

# create binary image with a square
def generate_square_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    start = size // 3
    end = size - start
    for x in range(start, end):
        for y in range(start, end):
            image[x][y] = 1  # set pixel to white (square)
    return image

# create a binary image with a diagonal line
def generate_line_image(size=8):
    image = [[0] * size for _ in range(size)]  # 0 is background
    for i in range(size):
        image[i][i] = 1  # set pixel to white (line)
    return image

# convert a 2D image (list of lists) to a 1D list for perceptron
def flatten_image(image):
    return [pixel for row in image for pixel in row]

# ave a 2D image as a PPM3 file
def save_image_ppm(image, filename):
    height = len(image)
    width = len(image[0])
    with open(filename, 'w') as f:
        # PPM3 header
        f.write(f'P3\n{width} {height}\n255\n')
        for row in image:
            for pixel in row:
                color = '255 255 255' if pixel == 1 else '0 0 0'
                f.write(f'{color} ')
            f.write('\n')

# generate and save training and testing data
def generate_and_save_data(num_samples=100, size=8):
    # dirs save images
    if not os.path.exists("train/circle"):
        os.makedirs("train/circle")
    if not os.path.exists("train/square"):
        os.makedirs("train/square")
    if not os.path.exists("train/line"):
        os.makedirs("train/line")
    if not os.path.exists("test/circle"):
        os.makedirs("test/circle")
    if not os.path.exists("test/square"):
        os.makedirs("test/square")
    if not os.path.exists("test/line"):
        os.makedirs("test/line")

    for i in range(num_samples):
        # create and save training images
        for shape, folder in zip(["circle", "square", "line"], ["train/circle", "train/square", "train/line"]):
            if shape == "circle":
                image = generate_circle_image(size)
            elif shape == "square":
                image = generate_square_image(size)
            elif shape == "line":
                image = generate_line_image(size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")
        
        # create and save testing images (more samples for testing)
        for shape, folder in zip(["circle", "square", "line"], ["test/circle", "test/square", "test/line"]):
            if shape == "circle":
                image = generate_circle_image(size)
            elif shape == "square":
                image = generate_square_image(size)
            elif shape == "line":
                image = generate_line_image(size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")

generate_and_save_data()
