from PIL import Image

class OutputBuffer:
    def __init__(self, width: int, height: int):
        """Initialize an output buffer of given width and height."""
        self.width = width
        self.height = height
        # Create a new image with white background (255, 255, 255)
        self.image = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        self.pixels = self.image.load()

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        """Set the pixel at (x, y) to the given color (RGB)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[x, y] = color
        else:
            raise ValueError(f"Pixel coordinates ({x}, {y}) are out of bounds.")

    def clear(self):
        """Clear the output buffer (set all pixels to white)."""
        for x in range(self.width):
            for y in range(self.height):
                self.pixels[x, y] = (255, 255, 255)  # Set each pixel to white

    def save(self, filename: str):
        """Save the current image to a file."""
        self.image.save(filename)



    # for testing purposes!
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, color: tuple[int, int, int]):
        """Draw a filled rectangle from (x1, y1) to (x2, y2) with the given color."""
        for x in range(x1, x2):
            for y in range(y1, y2):
                self.set_pixel(x, y, color)
