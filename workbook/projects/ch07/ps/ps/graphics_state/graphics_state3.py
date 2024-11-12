from PIL import Image, ImageDraw
import math


class Transformations:
    @staticmethod
    def translate(matrix: list[list[float]], dx: float, dy: float) -> list[list[float]]:
        translation_matrix = [
            [1, 0, dx],
            [0, 1, dy],
            [0, 0, 1]
        ]
        return matrix_multiply(matrix, translation_matrix)

    @staticmethod
    def rotate(matrix: list[list[float]], angle: float) -> list[list[float]]:
        # Convert angle to radians
        angle_rad = math.radians(angle)
        rotation_matrix = [
            [math.cos(angle_rad), -math.sin(angle_rad), 0],
            [math.sin(angle_rad), math.cos(angle_rad), 0],
            [0, 0, 1]
        ]
        return matrix_multiply(matrix, rotation_matrix)

    @staticmethod
    def scale(matrix: list[list[float]], sx: float, sy: float) -> list[list[float]]:
        scaling_matrix = [
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ]
        return matrix_multiply(matrix, scaling_matrix)

    @staticmethod
    def shear(matrix: list[list[float]], sx: float, sy: float) -> list[list[float]]:
        shear_matrix = [
            [1, sx, 0],
            [sy, 1, 0],
            [0, 0, 1]
        ]
        return matrix_multiply(matrix, shear_matrix)


# Helper function for matrix multiplication
def matrix_multiply(a, b):
    result = [[0 for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            result[i][j] = sum(a[i][k] * b[k][j] for k in range(len(b)))
    return result


class GraphicsState:
    def __init__(self):
        self.current_color = (0, 0, 0)  # Default color is black
        self.current_line_width = 1.0  # Default line width
        self.current_transform = [
            [1, 0, 0],  # Identity matrix for transformation
            [0, 1, 0],
            [0, 0, 1]
        ]
        
    def set_color(self, r: int, g: int, b: int):
        """Sets the current drawing color."""
        self.current_color = (r, g, b)

    def set_line_width(self, width: float):
        """Sets the current line width."""
        self.current_line_width = width

    def apply_transform(self, transform_function, *args):
        """Applies a transformation function (translate, rotate, scale) to the current transformation matrix."""
        self.current_transform = transform_function(self.current_transform, *args)

    def get_transformed_points(self, points):
        """Applies the current transformation matrix to a list of points (in homogeneous coordinates)."""
        transformed_points = []
        for (x, y) in points:
            # Convert to homogeneous coordinates (x, y, 1)
            new_x = self.current_transform[0][0] * x + self.current_transform[0][1] * y + self.current_transform[0][2]
            new_y = self.current_transform[1][0] * x + self.current_transform[1][1] * y + self.current_transform[1][2]
            transformed_points.append((new_x, new_y))
        return transformed_points




def draw_transformed_rectangles(image_size=(400, 400)):
    # Create a blank white image
    image = Image.new('RGB', image_size, (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Define a simple rectangle's corner points (in original position)
    rect_points = [(100, 100), (300, 100), (300, 300), (100, 300)]

    # Create a graphics state object
    graphics_state = GraphicsState()

    # Draw the original rectangle in black
    graphics_state.set_color(0, 0, 0)
    transformed_points = graphics_state.get_transformed_points(rect_points)
    draw.polygon(transformed_points, outline=graphics_state.current_color, width=int(graphics_state.current_line_width))

    # Apply transformations and draw rectangles with different colors
    # Apply translation (move the rectangle 100 units to the right and 50 units down)
    graphics_state.set_color(255, 0, 0)  # Red color
    graphics_state.apply_transform(Transformations.translate, 100, 50)
    transformed_points = graphics_state.get_transformed_points(rect_points)
    draw.polygon(transformed_points, outline=graphics_state.current_color, width=int(graphics_state.current_line_width))

    # Apply rotation (rotate the rectangle by 45 degrees)
    graphics_state.set_color(0, 255, 0)  # Green color
    graphics_state.apply_transform(Transformations.rotate, 45)
    transformed_points = graphics_state.get_transformed_points(rect_points)
    draw.polygon(transformed_points, outline=graphics_state.current_color, width=int(graphics_state.current_line_width))

    # Apply scaling (scale by 1.5 in x and y)
    graphics_state.set_color(0, 0, 255)  # Blue color
    graphics_state.apply_transform(Transformations.scale, 1.5, 1.5)
    transformed_points = graphics_state.get_transformed_points(rect_points)
    draw.polygon(transformed_points, outline=graphics_state.current_color, width=int(graphics_state.current_line_width))

    # Apply shear (shear by 0.5 in the x-direction)
    graphics_state.set_color(255, 165, 0)  # Orange color
    graphics_state.apply_transform(Transformations.shear, 0.5, 0)
    transformed_points = graphics_state.get_transformed_points(rect_points)
    draw.polygon(transformed_points, outline=graphics_state.current_color, width=int(graphics_state.current_line_width))

# Add this to the existing code within the draw_transformed_rectangles function

    # Draw a line with different thicknesses
    line_start = (50, 50)
    line_end = (350, 50)

    # Draw line with thickness 1 (default)
    graphics_state.set_line_width(1.0)  # Thin line
    graphics_state.set_color(0, 0, 0)  # Black color
    draw.line([line_start, line_end], fill=graphics_state.current_color, width=int(graphics_state.current_line_width))

    # Draw line with thickness 5
    graphics_state.set_line_width(5.0)  # Thick line
    graphics_state.set_color(255, 0, 0)  # Red color
    draw.line([line_start, line_end], fill=graphics_state.current_color, width=int(graphics_state.current_line_width))

    # Draw line with thickness 10
    graphics_state.set_line_width(10.0)  # Very thick line
    graphics_state.set_color(0, 255, 0)  # Green color
    draw.line([line_start, line_end], fill=graphics_state.current_color, width=int(graphics_state.current_line_width))

    # Save the resulting image to a file
    image.save('transformed_rectangles.png')
    print("Image saved as 'transformed_rectangles.png'.")

# Run the drawing function
draw_transformed_rectangles()
