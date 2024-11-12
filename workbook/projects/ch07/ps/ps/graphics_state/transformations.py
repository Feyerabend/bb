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

# Helper function for matrix multiplication
def matrix_multiply(a, b):
    result = [[0 for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            result[i][j] = sum(a[i][k] * b[k][j] for k in range(len(b)))
    return result

# Example of using the transformations
matrix = [
    [1, 0, 0],  # A point (x, y, 1) in homogeneous coordinates
    [0, 1, 0],
    [0, 0, 1]
]
