import math

class Path:
    def __init__(self):
        # Store the path segments
        self.commands = []

    def moveto(self, x: float, y: float):
        """Move the pen to a new starting point without drawing anything."""
        self.commands.append(('moveto', x, y))

    def lineto(self, x: float, y: float):
        """Draw a straight line from the current point to (x, y)."""
        self.commands.append(('lineto', x, y))

    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        """Draw a cubic Bézier curve from the current point using control points (x1, y1), (x2, y2), (x3, y3)."""
        self.commands.append(('curveto', x1, y1, x2, y2, x3, y3))

    def closepath(self):
        """Close the path (return to the starting point of the path)."""
        self.commands.append(('closepath',))

    def draw(self):
        """Simulate the drawing of the path."""
        path_representation = ""
        for command in self.commands:
            if command[0] == 'moveto':
                path_representation += f"Move to: ({command[1]}, {command[2]})\n"
            elif command[0] == 'lineto':
                path_representation += f"Draw line to: ({command[1]}, {command[2]})\n"
            elif command[0] == 'curveto':
                path_representation += f"Draw cubic Bézier curve with control points: ({command[1]}, {command[2]}) -> ({command[3]}, {command[4]}) -> ({command[5]}, {command[6]})\n"
            elif command[0] == 'closepath':
                path_representation += "Close path\n"
        return path_representation

    def get_path_data(self):
        """Return the path data for inspection."""
        return self.commands
