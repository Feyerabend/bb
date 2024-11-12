import math

class GraphicsState:
    def __init__(self):

        self.current_color = (0, 0, 0)  # black
        self.current_line_width = 1.0   # line width
        self.current_transform = [[1, 0, 0],  # identity matrix
                                  [0, 1, 0],
                                  [0, 0, 1]]
        self.state_stack = [] # incl. CTM

    def set_color(self, r: int, g: int, b: int):
        self.current_color = (r, g, b)
        print(f"Color set to: {self.current_color}")

    def set_line_width(self, width: float):
        self.current_line_width = width
        print(f"Line width set to: {self.current_line_width}")

    def apply_transform(self, matrix: list[list[float]]):
        self.current_transform = self.matrix_multiply(self.current_transform, matrix)
        print(f"Applied transformation, new CTM: {self.current_transform}")

    def push_state(self):
        state = {
            'color': self.current_color,
            'line_width': self.current_line_width,
            'transform': self.copy_matrix(self.current_transform)
        }
        self.state_stack.append(state)
        print("State pushed to stack.")

    def pop_state(self):
        if self.state_stack:
            state = self.state_stack.pop()
            self.current_color = state['color']
            self.current_line_width = state['line_width']
            self.current_transform = state['transform']
            print("State popped from stack.")
        else:
            print("No state to pop.")

    def matrix_multiply(self, mat1, mat2):
        result = [[0, 0, 0] for _ in range(3)]
        
        for i in range(3):
            for j in range(3):
                result[i][j] = sum(mat1[i][k] * mat2[k][j] for k in range(3))
        
        return result

    def copy_matrix(self, matrix):
        return [row[:] for row in matrix]

    def translation_matrix(self, dx, dy):
        return [
            [1, 0, dx],
            [0, 1, dy],
            [0, 0, 1]
        ]

    def scaling_matrix(self, sx, sy):
        return [
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ]
    
    def rotation_matrix(self, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        return [
            [math.cos(angle_radians), -math.sin(angle_radians), 0],
            [math.sin(angle_radians), math.cos(angle_radians), 0],
            [0, 0, 1]
        ]
    
    def shearing_matrix(self, shx, shy):
        return [
            [1, shx, 0],
            [shy, 1, 0],
            [0, 0, 1]
        ]

# Example usage:
graphics_state = GraphicsState()

# Set the initial color and line width
graphics_state.set_color(255, 0, 0)  # Red
graphics_state.set_line_width(2.0)

# Apply a scaling transformation (scale by 2 in both x and y directions)
scaling_matrix = graphics_state.scaling_matrix(2, 2)
graphics_state.apply_transform(scaling_matrix)

# Apply a rotation transformation (rotate by 45 degrees)
rotation_matrix = graphics_state.rotation_matrix(45)
graphics_state.apply_transform(rotation_matrix)

# Apply a translation transformation (move by 50 units in x and 30 in y)
translation_matrix = graphics_state.translation_matrix(50, 30)
graphics_state.apply_transform(translation_matrix)

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
