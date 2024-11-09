import unittest
import math
from transformations import Transformations, matrix_multiply

class TestTransformations(unittest.TestCase):
    def setUp(self):
        # Set up a simple identity matrix for testing
        self.identity_matrix = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]

    def test_translate(self):
        dx, dy = 3, 4
        expected_matrix = [
            [1, 0, 3],
            [0, 1, 4],
            [0, 0, 1]
        ]
        result = Transformations.translate(self.identity_matrix, dx, dy)
        self.assertEqual(result, expected_matrix)

    def test_rotate_90_degrees(self):
        angle = 90  # 90 degrees counterclockwise
        expected_matrix = [
            [0, -1, 0],
            [1,  0, 0],
            [0,  0, 1]
        ]
        result = Transformations.rotate(self.identity_matrix, angle)
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(result[i][j], expected_matrix[i][j], places=5)

    def test_rotate_45_degrees(self):
        angle = 45
        expected_matrix = [
            [math.cos(math.radians(45)), -math.sin(math.radians(45)), 0],
            [math.sin(math.radians(45)), math.cos(math.radians(45)), 0],
            [0, 0, 1]
        ]
        result = Transformations.rotate(self.identity_matrix, angle)
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(result[i][j], expected_matrix[i][j], places=5)

    def test_scale(self):
        sx, sy = 2, 3
        expected_matrix = [
            [2, 0, 0],
            [0, 3, 0],
            [0, 0, 1]
        ]
        result = Transformations.scale(self.identity_matrix, sx, sy)
        self.assertEqual(result, expected_matrix)

def test_combined_transformations(self):
    # Apply translation, then rotation, then scaling
    matrix = self.identity_matrix
    matrix = Transformations.translate(matrix, 3, 4)
    matrix = Transformations.rotate(matrix, 90)
    matrix = Transformations.scale(matrix, 2, 3)

    expected_matrix = [
        [0, -2, -4],
        [3,  0, 6],
        [0,  0, 1]
    ]
    for i in range(3):
        for j in range(3):
            self.assertAlmostEqual(matrix[i][j], expected_matrix[i][j], places=5)

# Run the tests
if __name__ == '__main__':
    unittest.main()