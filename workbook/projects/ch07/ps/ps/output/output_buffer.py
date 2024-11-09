from PIL import Image
from abc import ABC, abstractmethod

class ImageFormat(ABC):
    @abstractmethod
    def save(self, filename: str):
        pass

class PPMImage(ImageFormat):
    def __init__(self, buffer):
        self.buffer = buffer  # OutputBuffer instance

    def save(self, filename: str):
        with open(filename, "w") as f:
            width, height = self.buffer.width, self.buffer.height
            f.write(f"P3\n{width} {height}\n255\n")  # PPM header ASCII
            for y in range(height):
                for x in range(width):
                    r, g, b = self.buffer.get_pixel(x, y)
                    f.write(f"{r} {g} {b} ")
                f.write("\n")

class PNGImage(ImageFormat):
    def __init__(self, buffer):
        self.buffer = buffer

    def save(self, filename: str):
        img = Image.new("RGB", (self.buffer.width, self.buffer.height))
        for y in range(self.buffer.height):
            for x in range(self.buffer.width):
                color = self.buffer.get_pixel(x, y)
                img.putpixel((x, y), color)
        img.save(filename, "PNG")

class JPEGImage(ImageFormat):
    def __init__(self, buffer):
        self.buffer = buffer

    def save(self, filename: str):
        img = Image.new("RGB", (self.buffer.width, self.buffer.height))
        for y in range(self.buffer.height):
            for x in range(self.buffer.width):
                color = self.buffer.get_pixel(x, y)
                img.putpixel((x, y), color)
        img.save(filename, "JPEG")

class BMPImage(ImageFormat):
    def __init__(self, buffer):
        self.buffer = buffer

    def save(self, filename: str):
        img = Image.new("RGB", (self.buffer.width, self.buffer.height))
        for y in range(self.buffer.height):
            for x in range(self.buffer.width):
                color = self.buffer.get_pixel(x, y)
                img.putpixel((x, y), color)
        img.save(filename, "BMP")

class TIFFImage(ImageFormat):
    def __init__(self, buffer):
        self.buffer = buffer

    def save(self, filename: str):
        img = Image.new("RGB", (self.buffer.width, self.buffer.height))
        for y in range(self.buffer.height):
            for x in range(self.buffer.width):
                color = self.buffer.get_pixel(x, y)
                img.putpixel((x, y), color)
        img.save(filename, "TIFF")

class OutputBuffer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pixels = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]  # init white pixels

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        self.pixels[y][x] = color

    def clear(self):
        self.pixels = [[(255, 255, 255) for _ in range(self.width)] for _ in range(self.height)]

    def get_pixel(self, x: int, y: int):
        return self.pixels[y][x]

    def save(self, filename: str, format: str):
        if format.lower() == "ppm":
            image = PPMImage(self)
        elif format.lower() == "png":
            image = PNGImage(self)
        elif format.lower() == "jpeg":
            image = JPEGImage(self)
        elif format.lower() == "bmp":
            image = BMPImage(self)
        elif format.lower() == "tiff":
            image = TIFFImage(self)
        else:
            raise ValueError("Unsupported format")

        image.save(filename)


# Create an OutputBuffer with a width and height
buffer = OutputBuffer(800, 600)

# Set some pixels (example)
buffer.set_pixel(10, 10, (255, 0, 0))  # Red
buffer.set_pixel(20, 20, (0, 255, 0))  # Green
buffer.set_pixel(30, 30, (0, 0, 255))  # Blue

# Save as PPM
buffer.save("output.ppm", "ppm")

# Save as PNG
buffer.save("output.png", "png")

# Save as JPEG
buffer.save("output.jpg", "jpeg")

