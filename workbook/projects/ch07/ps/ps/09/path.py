from abc import ABC, abstractmethod

class PathCommand(ABC):
    @abstractmethod
    def execute(self, path: 'Path'):  # 'Path' as fwd decl
        pass

class DrawStrategy(ABC):
    @abstractmethod
    def draw(self, path: 'Path'):
        pass

class RasterDrawStrategy(DrawStrategy):
    def draw(self, path: 'Path'):
        print("Raster drawing of path")

class VectorDrawStrategy(DrawStrategy):
    def draw(self, path: 'Path'):
        print("Vector drawing of path")

class Path:
    def __init__(self, draw_strategy=None):
        self.commands = []
        if draw_strategy:
            self.draw_strategy = draw_strategy
        else:
            self.draw_strategy = RasterDrawStrategy() # default

    def moveto(self, x: float, y: float):
        print(f"Move to: ({x}, {y})")

    def lineto(self, x: float, y: float):
        print(f"Draw line to: ({x}, {y})")

    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        print(f"Draw cubic Bézier curve: ({x1}, {y1}) -> ({x2}, {y2}) -> ({x3}, {y3})")

    def execute_command(self, command: PathCommand):
        command.execute(self)

    def set_draw_strategy(self, strategy: DrawStrategy):
        self.draw_strategy = strategy

    def draw(self):
        self.draw_strategy.draw(self)

    # Additional methods like moveto, lineto, etc.



# Usage
#path = Path(RasterDrawStrategy())  # Start with raster
#path.draw()

# Switch to vector strategy
#path.set_draw_strategy(VectorDrawStrategy())
#path.draw()



class MovetoCommand(PathCommand):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def execute(self, path: 'Path'):
        path.moveto(self.x, self.y)

class LinetoCommand(PathCommand):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def execute(self, path: 'Path'):
        path.lineto(self.x, self.y)

class CurvetoCommand(PathCommand):
    def __init__(self, x1, y1, x2, y2, x3, y3):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

    def execute(self, path: 'Path'):
        path.curveto(self.x1, self.y1, self.x2, self.y2, self.x3, self.y3)

# Usage example
#path = Path()

# Create commands
#moveto = MovetoCommand(10, 10)
#lineto = LinetoCommand(100, 100)

# Execute commands
#path.execute_command(moveto)
#path.execute_command(lineto)



class CompositePath(Path):
    def __init__(self):
        super().__init__()
        self.paths = []

    def add(self, path: Path):
        self.paths.append(path)

    def execute_command(self, command: PathCommand):
        super().execute_command(command)
        for path in self.paths:
            path.execute_command(command)

# Usage
#path1 = Path()
#path2 = Path()
#composite_path = CompositePath()

# Add paths to composite
#composite_path.add(path1)
#composite_path.add(path2)

# Execute commands on all paths in the composite
#composite_path.execute_command(moveto)
#composite_path.execute_command(lineto)








# Usage
#path = Path()

# Create commands
#moveto = MovetoCommand(10, 10)
#lineto = LinetoCommand(100, 100)
#curveto = CurvetoCommand(50, 150, 150, 50, 200, 100)

# Execute commands
#path.execute_command(moveto)
#path.execute_command(lineto)
#path.execute_command(curveto)

