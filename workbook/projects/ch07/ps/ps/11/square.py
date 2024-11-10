import math
from PIL import Image, ImageDraw


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
    def shear_x(matrix: list[list[float]], sx: float) -> list[list[float]]:
        shear_x_matrix = [
            [1, sx, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
        return matrix_multiply(matrix, shear_x_matrix)

    @staticmethod
    def shear_y(matrix: list[list[float]], sy: float) -> list[list[float]]:
        shear_y_matrix = [
            [1, 0, 0],
            [sy, 1, 0],
            [0, 0, 1]
        ]
        return matrix_multiply(matrix, shear_y_matrix)


# Helper function for matrix multiplication
def matrix_multiply(a, b):
    result = [[0 for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            result[i][j] = sum(a[i][k] * b[k][j] for k in range(len(b)))
    return result


# Function to draw a square on an image
def draw_square(image: Image, matrix: list[list[float]], color: tuple, offset: tuple = (0, 0)):
    draw = ImageDraw.Draw(image)

    # Define the vertices of a unit square (centered at (0,0))
    square_vertices = [
        [-50, -50, 1],  # Top-left corner
        [ 50, -50, 1],  # Top-right corner
        [ 50,  50, 1],  # Bottom-right corner
        [-50,  50, 1],  # Bottom-left corner
    ]

    # Apply the transformation to each vertex of the square
    transformed_vertices = []
    for vertex in square_vertices:
        transformed_vertex = matrix_multiply([vertex], matrix)[0]
        transformed_vertices.append(transformed_vertex)

    # Draw lines between the transformed vertices
    for i in range(4):
        x0, y0, _ = transformed_vertices[i]
        x1, y1, _ = transformed_vertices[(i + 1) % 4]
        draw.line([(x0 + image.width // 2 + offset[0], y0 + image.height // 2 + offset[1]), 
                   (x1 + image.width // 2 + offset[0], y1 + image.height // 2 + offset[1])], 
                  fill=color, width=2)


# Function to create an image with the transformed square
def create_transformed_image(width: int, height: int, transformations: list, color: tuple, original_color: tuple):
    # Create a blank white image
    image = Image.new("RGB", (width, height), (255, 255, 255))
    
    # Initial identity matrix (no transformation)
    matrix = [
        [1, 0, 0],  # X-axis scaling
        [0, 1, 0],  # Y-axis scaling
        [0, 0, 1]   # Homogeneous coordinate
    ]
    
    # Draw the original square in blue
    draw_square(image, matrix, original_color)

    # Apply each transformation in sequence
    for transform in transformations:
        matrix = transform(matrix)
    
    # Draw the transformed square in red
    draw_square(image, matrix, color)
    
    return image


# Example of using the transformations to manipulate the square
if __name__ == "__main__":
    # Set the image size
    width, height = 400, 400

    # Define the transformations to apply
    transformations = [
        lambda matrix: Transformations.translate(matrix, 50, 100),  # Translate by (50, 100)
        lambda matrix: Transformations.rotate(matrix, 45),  # Rotate by 45 degrees
        lambda matrix: Transformations.scale(matrix, 1.5, 1.5),  # Scale by 1.5
        lambda matrix: Transformations.shear_x(matrix, 0.5),  # Shear in X direction
        lambda matrix: Transformations.shear_y(matrix, 0.5),  # Shear in Y direction
    ]
    
    # Create the image with the transformed square
    image = create_transformed_image(width, height, transformations, color=(255, 0, 0), original_color=(0, 0, 255))

    # Save the image as PNG
    image.save("transformed_and_original_squares.png")
    image.show()  # Optionally display the image