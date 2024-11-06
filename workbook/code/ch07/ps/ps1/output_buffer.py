# output_buffer.py
class OutputBuffer:
    def __init__(self, width: int, height: int):
        self.width = width  # Initialize with given width
        self.height = height  # Initialize with given height
        # Initialize pixels with white color
        self.pixels = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color  # Set pixel color

    def display(self):
        for row in self.pixels:
            print("".join("█" if pixel == (255, 0, 0) else " " for pixel in row))
