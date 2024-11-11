from PIL import Image

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

# Test gradient blending using PIL
def test_gradient_blending_pillow():
    color1 = (255, 0, 0)  # Red
    color2 = (0, 0, 255)  # Blue
    width = 500
    height = 50  # Height of the gradient strip

    # Create a new image with RGB mode
    image = Image.new("RGB", (width, height))

    # Loop through the image width and calculate the blended color at each pixel
    for x in range(width):
        ratio = x / (width - 1)  # Calculate the ratio from 0 to 1 based on x position
        blended_color = ColorUtils.blend_colors(color1, color2, ratio)
        for y in range(height):  # Fill the whole height with the same color
            image.putpixel((x, y), blended_color)

    # Save or display the image
    image.show()  # To display the image
    image.save("gradient_blend.png")  # Optionally save the image

# Run the test
test_gradient_blending_pillow()
