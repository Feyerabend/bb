# interpreter.py
from draw import draw_line, draw_bezier_curve, draw_cubic_bezier_curve, draw_line_with_sampling, draw_line_with_anti_aliasing
from ppm import save_ppm
import numpy as np

class SimpleRasterizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]  # RGB image initialized to black

    def moveto(self, x, y):
        self.current_pos = (x, y)

    def lineto(self, x, y, color=(255, 0, 0)):
        #draw_line(self.image, self.current_pos, (x, y), color)
        #draw_line_with_anti_aliasing(self.image, self.current_pos, (x, y), color)
        draw_line_with_sampling(self.image, self.current_pos, (x, y), color)
        self.current_pos = (x, y)

    def bezier(self, p1, p2, p3, color=(0, 255, 0)):
        draw_bezier_curve(self.image, p1, p2, p3, color)

    def beziercurve(self, p1, p2, p3, p4, color=(0, 255, 0)):
        draw_cubic_bezier_curve(self.image, p1, p2, p3, p4, color)

    def save(self, filename):
#        self.supersample(4)
        save_ppm(filename, self.width, self.height, self.image)

    def supersample(self, scale):
        original_height = len(self.image)
        original_width = len(self.image[0])
        # Create a larger image
        large_image = np.zeros((original_height * scale, original_width * scale, 3), dtype=int)

        # Fill the large image with the pixel values from the original image
        for y in range(original_height):
            for x in range(original_width):
                large_image[y * scale:(y + 1) * scale, x * scale:(x + 1) * scale] = self.image[y][x]

        # Average the pixels for anti-aliasing
        antialiased_image = np.zeros((original_height, original_width, 3), dtype=int)
        for y in range(original_height):
            for x in range(original_width):
                # Average the corresponding block in the large image
                antialiased_image[y][x] = np.mean(large_image[y * scale:(y + 1) * scale, x * scale:(x + 1) * scale], axis=(0, 1))

        return antialiased_image.astype(int)
