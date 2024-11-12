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

# GraphicsState Class
class GraphicsState:
    def __init__(self):
        # Initialize the graphics state with default values
        self.current_color = (0, 0, 0)  # Default color is black
        self.current_line_width = 1.0   # Default line width
        self.current_transform = [
            [1, 0, 0],  # Identity matrix for transformation
            [0, 1, 0],
            [0, 0, 1]
        ]
        
        # Stack to save and restore the graphics state
        self.state_stack = []

    def set_color(self, r: int, g: int, b: int):
        """Sets the current drawing color."""
        self.current_color = (r, g, b)
        print(f"Color set to: {self.current_color}")

    def set_line_width(self, width: float):
        """Sets the current line width."""
        self.current_line_width = width
        print(f"Line width set to: {self.current_line_width}")

    def apply_transform(self, transform_function, *args):
        """Applies a transformation function (translate, rotate, scale) to the current transformation matrix."""
        self.current_transform = transform_function(self.current_transform, *args)
        print(f"Applied transformation, new CTM: {self.current_transform}")

    def push_state(self):
        """Pushes the current graphics state (including CTM) onto the stack."""
        state = {
            'color': self.current_color,
            'line_width': self.current_line_width,
            'transform': self.copy_matrix(self.current_transform)
        }
        self.state_stack.append(state)
        print("State pushed to stack.")

    def pop_state(self):
        """Restores the last graphics state from the stack, including the CTM."""
        if self.state_stack:
            state = self.state_stack.pop()
            self.current_color = state['color']
            self.current_line_width = state['line_width']
            self.current_transform = state['transform']
            print("State popped from stack.")
        else:
            print("No state to pop.")

    def copy_matrix(self, matrix):
        """Creates a deep copy of the 3x3 matrix (used for saving state)."""
        return [row[:] for row in matrix]

# Example of usage
graphics_state = GraphicsState()

# Set the initial color and line width
graphics_state.set_color(255, 0, 0)  # Red
graphics_state.set_line_width(2.0)

# Apply a scaling transformation (scale by 2 in both x and y directions)
graphics_state.apply_transform(Transformations.scale, 2, 2)

# Apply a rotation transformation (rotate by 45 degrees)
graphics_state.apply_transform(Transformations.rotate, 45)

# Apply a translation transformation (move by 50 units in x and 30 in y)
graphics_state.apply_transform(Transformations.translate, 50, 30)

# Push the current state (including CTM) onto the stack
graphics_state.push_state()

# Change the state (e.g., change color to blue)
graphics_state.set_color(0, 0, 255)  # Blue

# Pop the state, restoring the previous graphics state (including CTM)
graphics_state.pop_state()

# Final check
print(f"Final color: {graphics_state.current_color}")
print(f"Final line width: {graphics_state.current_line_width}")
print(f"Final CTM: {graphics_state.current_transform}")
