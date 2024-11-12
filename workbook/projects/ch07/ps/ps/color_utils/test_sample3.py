from PIL import Image

class ColorUtils:
    @staticmethod
    def rgb_to_gray(r: int, g: int, b: int) -> int:
        return int(0.299 * r + 0.587 * g + 0.114 * b)

    @staticmethod
    def blend_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
        """
        Blend two colors with a given ratio.
        :param color1: First color (r1, g1, b1)
        :param color2: Second color (r2, g2, b2)
        :param ratio: Blending ratio between the two colors (0.0 to 1.0)
        :return: Blended color (r, g, b)
        """
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        return r, g, b

# Create an image based on blended colors
def create_blended_grid_image(width: int, height: int, block_size: int, color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float):
    # Create a new image
    img = Image.new('RGB', (width, height))
    
    # Access the image's pixel data
    pixels = img.load()
    
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            # Fill the blocks
            for i in range(x, min(x + block_size, width)):
                for j in range(y, min(y + block_size, height)):
                    if (i < x + block_size // 2 and j < y + block_size // 2):
                        # Left top half of the block, use color1 (red)
                        color = color1
                    elif (i >= x + block_size // 2 and j >= y + block_size // 2):
                        # Right bottom half of the block, use color2 (blue)
                        color = color2
                    else:
                        # Blended square in the middle: blend color1 and color2
                        blend_ratio_x = (i - x) / block_size  # ratio for x direction
                        blend_ratio_y = (j - y) / block_size  # ratio for y direction
                        # Average of the two ratios to get a smoother blend effect
                        blend_ratio = (blend_ratio_x + blend_ratio_y) / 2
                        color = ColorUtils.blend_colors(color1, color2, blend_ratio)

                    pixels[i, j] = color

    return img

# Example usage:
width, height = 300, 300  # Image dimensions
block_size = 50  # Size of each block
color1 = (0, 0, 0)  # Red
color2 = (255, 255, 255)  # Blue
ratio = 0.5  # Blend 50% of each color

# Generate the image with the blended grid
img = create_blended_grid_image(width, height, block_size, color1, color2, ratio)

# Save the image or display it
img.save('blended_grid_image_no_alpha.png')
img.show()