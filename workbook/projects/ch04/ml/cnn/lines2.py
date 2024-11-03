import numpy as np
from PIL import Image
import os

class CNNLineModel:
    def __init__(self, noise_level=30):  # Increase noise level for visibility
        self.noise_level = noise_level

    def generate_line_image(self, line_type, size=40):
        image = np.zeros((size, size), dtype=np.uint8)

        # Draw the line
        if line_type == 'horizontal':
            image[size // 2 - 2:size // 2 + 2, :] = 255
        elif line_type == 'vertical':
            image[:, size // 2 - 2:size // 2 + 2] = 255
        elif line_type == 'diagonal':
            np.fill_diagonal(image, 255)

        # Apply noise and print debug information
        noisy_image = self.add_noise(image)
        print(f"Generated {line_type} image with shape {noisy_image.shape}")
        return noisy_image

    def add_noise(self, image_array):
        # Gaussian noise for clear visibility
        noise = np.random.normal(0, self.noise_level, image_array.shape)
        noisy_image = np.clip(image_array + noise, 0, 255).astype(np.uint8)

        # Print noise sample for debug
        print("Sample noise values:", noise[0:2, 0:2])
        return noisy_image

    def save_image(self, image_array, filename):
        Image.fromarray(image_array).save(filename)

    def generate_and_save_noisy_images(self, line_types, num_images=5, size=40):
        os.makedirs("noisy_images", exist_ok=True)
        for line_type in line_types:
            for i in range(num_images):
                noisy_image = self.generate_line_image(line_type, size)
                filename = f"noisy_images/{line_type}_variation_{i+1}.png"
                self.save_image(noisy_image, filename)
                print(f"Saved noisy image: {filename}")

# Usage
line_types = ['horizontal', 'vertical', 'diagonal']
cnn_model = CNNLineModel(noise_level=30)  # Start with a high noise level for testing
cnn_model.generate_and_save_noisy_images(line_types)