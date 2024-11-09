from PIL import Image, ImageDraw

class ColorUtils:
    @staticmethod
    def rgb_to_gray(r: int, g: int, b: int) -> int:
        return int(0.299 * r + 0.587 * g + 0.114 * b)

    @staticmethod
    def blend_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        return r, g, b

# Create a blank image (white background)
width, height = 400, 300
image = Image.new('RGB', (width, height), (255, 255, 255))
draw = ImageDraw.Draw(image)

# 1. Drawing a solid red rectangle
red = (255, 0, 0)
draw.rectangle([50, 50, 150, 150], fill=red)

# 2. Blending two colors (red and blue) and drawing a rectangle with the blended color
blue = (0, 0, 255)
blended_color = ColorUtils.blend_colors(red, blue, 0.5)  # 50% blend
# Offsetting the blended rectangle to overlap with the red one
draw.rectangle([120, 50, 220, 150], fill=blended_color)

# 3. Converting a color to grayscale (green) and drawing a rectangle
green = (0, 255, 0)
gray_value = ColorUtils.rgb_to_gray(*green)
gray_color = (gray_value, gray_value, gray_value)  # Apply the same gray value to R, G, and B
# Offsetting the grayscale rectangle to overlap with the other ones
draw.rectangle([200, 50, 300, 150], fill=gray_color)

# 4. Saving the image
image.save('colored_rectangles_blended.png')

# Display the image (optional)
image.show()