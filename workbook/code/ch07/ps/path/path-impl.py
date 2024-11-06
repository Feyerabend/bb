from typing import List, Tuple, Union

class Path:
    def __init__(self):
        # Initializes an empty path with no commands or points
        self.path = []  # Stores a list of commands and their associated points
    
    def moveto(self, x: float, y: float):
        self.path.append(('moveto', (x, y)))
    
    def lineto(self, x: float, y: float):
        self.path.append(('lineto', (x, y)))
    
    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        self.path.append(('curveto', (x1, y1, x2, y2, x3, y3)))
    
    def closepath(self):
        self.path.append(('closepath', None))
    
    def __str__(self):
        path_str = []
        for command, points in self.path:
            if command == 'moveto':
                path_str.append(f"moveto {points[0]}, {points[1]}")
            elif command == 'lineto':
                path_str.append(f"lineto {points[0]}, {points[1]}")
            elif command == 'curveto':
                path_str.append(f"curveto {points[0]}, {points[1]}, {points[2]}, {points[3]}, {points[4]}, {points[5]}")
            elif command == 'closepath':
                path_str.append("closepath")
        return "\n".join(path_str)
    
    def get_path(self) -> List[Tuple[str, Union[Tuple[float, float], Tuple[float, float, float, float, float, float]]]]:
        return self.path

# Create a new Path object
path = Path()

# Move to a starting point
path.moveto(50, 50)

# Draw a line to a point
path.lineto(150, 50)

# Draw a cubic Bézier curve
path.curveto(100, 100, 200, 100, 150, 150)

# Close the path
path.closepath()

# Print out the path in string form
print(path)

# Get the full path with commands and points
full_path = path.get_path()
print("Full Path:", full_path)
