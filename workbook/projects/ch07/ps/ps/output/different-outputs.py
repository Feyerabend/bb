from PIL import Image

class OutputBuffer:
    def __init__(self, width: int, height: int):
        pass

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        pass

    def clear(self):
        pass

    def save(self, filename: str):
        pass

from PIL import Image

class PixelImage:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = Image.new("RGB", (width, height))
        
    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.image.putpixel((x, y), color)
    
    def fill_gradient(self, start_color: tuple[int, int, int], end_color: tuple[int, int, int], direction="horizontal"):
        """Fills the image with a gradient from start_color to end_color."""
        for y in range(self.height):
            for x in range(self.width):
                # Determine gradient position based on the direction
                if direction == "horizontal":
                    ratio = x / (self.width - 1)
                elif direction == "vertical":
                    ratio = y / (self.height - 1)
                else:
                    raise ValueError("Invalid direction. Use 'horizontal' or 'vertical'.")
                
                # Interpolate colors based on the ratio
                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                
                # Set the pixel to the interpolated color
                self.set_pixel(x, y, (r, g, b))

    def save(self, filename: str, format: str = "PNG"):
        """Saves the image to a file in the specified format."""
        self.image.save(filename, format=format)

# Usage example
# Create a 300x100 image with a horizontal gradient from red to blue
img = PixelImage(300, 100)
img.fill_gradient((255, 0, 0), (0, 0, 255), direction="horizontal")  # Red to Blue horizontally
img.save("gradient.png")  # Save as PNG




class GradientPPM:
    def __init__(self, width, height, start_color, end_color):
        self.width = width
        self.height = height
        self.start_color = start_color  # (R, G, B)
        self.end_color = end_color      # (R, G, B)
        self.pixels = []

    def generate_gradient(self):
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Interpolate between start_color and end_color based on x position
                r = int(self.start_color[0] + (self.end_color[0] - self.start_color[0]) * (x / self.width))
                g = int(self.start_color[1] + (self.end_color[1] - self.start_color[1]) * (x / self.width))
                b = int(self.start_color[2] + (self.end_color[2] - self.start_color[2]) * (x / self.width))
                row.append((r, g, b))
            self.pixels.append(row)

    def save_ppm(self, filename):
        with open(filename, 'w') as f:
            # Write PPM header
            f.write(f"P3\n{self.width} {self.height}\n255\n")
            # Write pixel data
            for row in self.pixels:
                for (r, g, b) in row:
                    f.write(f"{r} {g} {b} ")
                f.write("\n")

# Usage example:
# Start with red on the left and blue on the right for a horizontal gradient
start_color = (255, 0, 0)  # Red
end_color = (0, 0, 255)    # Blue
gradient_image = GradientPPM(300, 100, start_color, end_color)
gradient_image.generate_gradient()
gradient_image.save_ppm("gradient.ppm")
