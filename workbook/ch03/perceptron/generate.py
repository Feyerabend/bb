import os
import random

def generate_circle_image(size=8, noise_level=0.1):
    image = [[0] * size for _ in range(size)]
    cx, cy = random.randint(size // 4, 3 * size // 4), random.randint(size // 4, 3 * size // 4)
    radius = random.randint(size // 4, size // 3)
    
    for x in range(size):
        for y in range(size):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                image[x][y] = 1
    
    add_noise(image, noise_level)
    return image

def generate_square_image(size=8, noise_level=0.1):
    image = [[0] * size for _ in range(size)]
    start_x = random.randint(1, size // 3)
    start_y = random.randint(1, size // 3)
    end_x = random.randint(2 * size // 3, size - 1)
    end_y = random.randint(2 * size // 3, size - 1)
    
    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            image[x][y] = 1
    
    add_noise(image, noise_level)
    return image

def generate_line_image(size=8, noise_level=0.1):
    image = [[0] * size for _ in range(size)]
    x1, y1 = random.randint(0, size - 1), random.randint(0, size - 1)
    x2, y2 = random.randint(0, size - 1), random.randint(0, size - 1)
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    
    while True:
        image[x1][y1] = 1
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    
    add_noise(image, noise_level)
    return image

def add_noise(image, noise_level=0.1):
    size = len(image)
    num_pixels = int(size * size * noise_level)
    for _ in range(num_pixels):
        x, y = random.randint(0, size - 1), random.randint(0, size - 1)
        image[x][y] = 1 if image[x][y] == 0 else 0

def save_image_ppm(image, filename):
    height, width = len(image), len(image[0])
    with open(filename, 'w') as f:
        f.write(f'P3\n{width} {height}\n255\n')
        for row in image:
            for pixel in row:
                color = '255 255 255' if pixel == 1 else '0 0 0'
                f.write(f'{color} ')
            f.write('\n')

def generate_and_save_data(num_samples=100, size=8):
    for folder in ["train/circle", "train/square", "train/line", "test/circle", "test/square", "test/line"]:
        os.makedirs(folder, exist_ok=True)
    
    for i in range(num_samples):
        for shape, folder in zip(["circle", "square", "line"], ["train/circle", "train/square", "train/line"]):
            image = globals()[f'generate_{shape}_image'](size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")
        
        for shape, folder in zip(["circle", "square", "line"], ["test/circle", "test/square", "test/line"]):
            image = globals()[f'generate_{shape}_image'](size)
            save_image_ppm(image, f"{folder}/{shape}_{i}.ppm")

generate_and_save_data()
