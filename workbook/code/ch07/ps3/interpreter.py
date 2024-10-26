# interpreter.py

from draw import draw_line, draw_bezier_curve
from ppm import save_ppm

class SimpleRasterizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]  # RGB image initialized to black

    def moveto(self, x, y):
        self.current_pos = (x, y)

    def lineto(self, x, y, color=(255, 0, 0)):
        draw_line(self.image, self.current_pos, (x, y), color, sample_rate=4)
        self.current_pos = (x, y)

    def bezier(self, p1, p2, p3, color=(0, 255, 0)):
        draw_bezier_curve(self.image, p1, p2, p3, color, sample_rate=4)

    def save(self, filename):
        save_ppm(filename, self.width, self.height, self.image)