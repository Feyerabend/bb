import math
from PIL import Image, ImageDraw
from abc import ABC, abstractmethod
from typing import List, Tuple


# Component Interface
class Shape(ABC):
    @abstractmethod
    def get_points(self) -> List[List[float]]:
        pass
    
    def draw(self, image: Image.Image, color: tuple, offset: tuple = (0, 0)):
        draw = ImageDraw.Draw(image)
        points = self.get_points()
        
        # points to screen coordinates
        screen_points = []
        for x, y, _ in points:
            screen_x = x + image.width // 2 + offset[0]
            screen_y = y + image.height // 2 + offset[1]
            screen_points.append((screen_x, screen_y))
        
        # lines between the vertices
        for i in range(len(screen_points)):
            draw.line([screen_points[i], screen_points[(i + 1) % len(screen_points)]], 
                     fill=color, width=2)


# Concrete Component
class Square(Shape):
    def __init__(self, size: float = 50):
        self.size = size
        
    def get_points(self) -> List[List[float]]:
        half_size = self.size / 2
        # define the vertices of a square (centered at origin)
        return [
            [-half_size, -half_size, 1],  # top-left corner
            [ half_size, -half_size, 1],  # top-right corner
            [ half_size, half_size,  1],  # bottom-right corner
            [-half_size, half_size,  1],  # bottom-left corner
        ]


# Helper for matrix multiplication
def matrix_multiply(points, transformation_matrix):
    result = []
    for point in points:
        # point to a row matrix for multiplication
        point_matrix = [point]
        # multiply matrices
        new_point = [[0 for _ in range(len(transformation_matrix[0]))] for _ in range(len(point_matrix))]
        for i in range(len(point_matrix)):
            for j in range(len(transformation_matrix[0])):
                new_point[i][j] = sum(point_matrix[i][k] * transformation_matrix[k][j] 
                                     for k in range(len(transformation_matrix)))
        result.append(new_point[0])
    return result


# Base Decorator - abstract class that all decorators inherit from
class ShapeDecorator(Shape):
    def __init__(self, decorated_shape: Shape):
        self.decorated_shape = decorated_shape
    
    def get_points(self) -> List[List[float]]:
        # By default, return the decorated shape's points
        # Concrete decorators will override this method
        return self.decorated_shape.get_points()


# Concrete Decorators
class TranslateDecorator(ShapeDecorator):
    def __init__(self, decorated_shape: Shape, dx: float, dy: float):
        super().__init__(decorated_shape)
        self.dx = dx
        self.dy = dy
        
    def get_points(self) -> List[List[float]]:
        points = self.decorated_shape.get_points()
        translation_matrix = [
            [1, 0, self.dx],
            [0, 1, self.dy],
            [0, 0, 1]
        ]
        return matrix_multiply(points, translation_matrix)


class RotateDecorator(ShapeDecorator):
    def __init__(self, decorated_shape: Shape, angle: float):
        super().__init__(decorated_shape)
        self.angle = angle
        
    def get_points(self) -> List[List[float]]:
        points = self.decorated_shape.get_points()
        angle_rad = math.radians(self.angle)
        rotation_matrix = [
            [math.cos(angle_rad), -math.sin(angle_rad), 0],
            [math.sin(angle_rad), math.cos(angle_rad), 0],
            [0, 0, 1]
        ]
        return matrix_multiply(points, rotation_matrix)


class ScaleDecorator(ShapeDecorator):
    def __init__(self, decorated_shape: Shape, sx: float, sy: float):
        super().__init__(decorated_shape)
        self.sx = sx
        self.sy = sy
        
    def get_points(self) -> List[List[float]]:
        points = self.decorated_shape.get_points()
        scaling_matrix = [
            [self.sx, 0, 0],
            [0, self.sy, 0],
            [0, 0, 1]
        ]
        return matrix_multiply(points, scaling_matrix)


class ShearXDecorator(ShapeDecorator):
    def __init__(self, decorated_shape: Shape, sx: float):
        super().__init__(decorated_shape)
        self.sx = sx
        
    def get_points(self) -> List[List[float]]:
        points = self.decorated_shape.get_points()
        shear_matrix = [
            [1, self.sx, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
        return matrix_multiply(points, shear_matrix)


class ShearYDecorator(ShapeDecorator):
    def __init__(self, decorated_shape: Shape, sy: float):
        super().__init__(decorated_shape)
        self.sy = sy
        
    def get_points(self) -> List[List[float]]:
        points = self.decorated_shape.get_points()
        shear_matrix = [
            [1, 0, 0],
            [self.sy, 1, 0],
            [0, 0, 1]
        ]
        return matrix_multiply(points, shear_matrix)


# create an image with the transformed shape
def create_transformed_image(width: int, height: int, original_shape: Shape, decorated_shape: Shape, 
                            original_color: tuple, transformed_color: tuple):
    # create a blank white image
    image = Image.new("RGB", (width, height), (255, 255, 255))
    
    # draw original shape
    original_shape.draw(image, original_color)
    
    # draw transformed shape
    decorated_shape.draw(image, transformed_color)
    
    return image


# example of using the decorators to create transformations
if __name__ == "__main__":
    # Set image size
    width, height = 600, 600
    
    # Create original shape
    original_shape = Square(100)
    
    # Create a decorated shape with multiple transformations
    # Notice how we can nest decorators to apply multiple transformations
    # Transformations are applied from innermost to outermost
    transformed_shape = TranslateDecorator(
        RotateDecorator(
            ScaleDecorator(
                original_shape,
                1.5, 1.5  # Scale by 1.5
            ),
            45  # Rotate by 45 degrees
        ),
        100, 50  # Translate by (100, 50)
    )
    
    # Create the image with the original and transformed shapes
    image = create_transformed_image(
        width, height, 
        original_shape, transformed_shape,
        (0, 0, 255),  # Original in blue
        (255, 0, 0)   # Transformed in red
    )
    
    image.save("decorated_shapes.png")
    print("Created image: decorated_shapes.png")
    
    # Let's create a different sequence of transformations
    alternative_shape = ScaleDecorator(
        TranslateDecorator(
            RotateDecorator(
                Square(100),
                30  # Rotate by 30 degrees
            ),
            -100, 50  # Translate by (-100, 50)
        ),
        2.0, 1.0  # Scale by (2.0, 1.0) - stretching horizontally
    )
    
    # Create another image with the original and alternative transformed shapes
    alt_image = create_transformed_image(
        width, height, 
        original_shape, alternative_shape,
        (0, 0, 255),    # Original in blue
        (0, 128, 0)     # Alternative in green
    )
    
    alt_image.save("decorated_shapes_alternative.png")
    print("Created image: decorated_shapes_alternative.png")

    # Create a more complex example with a multi-shape pattern
    def create_multi_shape_demo():
        width, height = 800, 800
        image = Image.new("RGB", (width, height), (255, 255, 255))
        
        # Original square in the center
        base_square = Square(40)
        base_square.draw(image, (0, 0, 0))
        
        # Create 8 decorated squares around it
        for i in range(8):
            angle = i * 45  # 45 degrees apart
            distance = 150
            
            # Calc position based on angle
            dx = distance * math.cos(math.radians(angle))
            dy = distance * math.sin(math.radians(angle))
            
            # Create a decorated square with different transformations
            decorated = TranslateDecorator(
                RotateDecorator(
                    ScaleDecorator(
                        base_square,
                        1.5, 0.75  # Scale non-uniformly
                    ),
                    angle  # Rotate by the angle
                ),
                dx, dy  # Translate to position
            )
            
            # Draw with a color that varies with the angle
            r = int(128 + 127 * math.cos(math.radians(angle)))
            g = int(128 + 127 * math.sin(math.radians(angle)))
            b = int(128 + 127 * math.cos(math.radians(angle + 90)))
            
            decorated.draw(image, (r, g, b))
        
        image.save("decorated_pattern.png")
        print("Created image: decorated_pattern.png")

    create_multi_shape_demo()