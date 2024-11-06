class Path:
    def __init__(self):
        self.commands = []

    def moveto(self, x: float, y: float):
        self.commands.append(('moveto', (x, y)))

    def lineto(self, x: float, y: float):
        self.commands.append(('lineto', (x, y)))

    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        self.commands.append(('curveto', (x1, y1, x2, y2, x3, y3)))

    def closepath(self):
        self.commands.append(('closepath', None))

    def get_path(self):
        return self.commands


class PathExecutor:
    def __init__(self, path: Path):
        self.path = path
        self.current_position = (0, 0)  # Start at origin by default
    
    def execute(self):
        """
        Execute all commands in the path.
        """
        for command, points in self.path.get_path():
            if command == 'moveto':
                self.moveto(*points)
            elif command == 'lineto':
                self.lineto(*points)
            elif command == 'curveto':
                self.curveto(*points)
            elif command == 'closepath':
                self.closepath()
    
    def moveto(self, x: float, y: float):
        """
        Move the pen to the new coordinates (x, y).
        """
        self.current_position = (x, y)
        print(f"Move to: {self.current_position}")
    
    def lineto(self, x: float, y: float):
        """
        Draw a line to (x, y) from the current position.
        """
        print(f"Line to: {x}, {y} (from {self.current_position})")
        self.current_position = (x, y)
    
    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        """
        Draw a cubic Bézier curve from the current position to (x3, y3) using
        control points (x1, y1) and (x2, y2).
        """
        print(f"Bezier curve from {self.current_position} to ({x3}, {y3}) with control points ({x1}, {y1}), ({x2}, {y2})")
        self.current_position = (x3, y3)
    
    def closepath(self):
        """
        Close the path by drawing a line back to the start position.
        """
        print(f"Close path. Line back to the starting position.")
        self.current_position = self.path.get_path()[0][1]  # The starting position from the first moveto

# Example Usage
path = Path()
path.moveto(50, 50)
path.lineto(150, 50)
path.curveto(100, 100, 200, 100, 150, 150)
path.closepath()

# Create a PathExecutor and execute the path
executor = PathExecutor(path)
executor.execute()