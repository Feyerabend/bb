from abc import ABC, abstractmethod

class PathCommand(ABC):
    @abstractmethod
    def execute(self, path: 'Path'):  # 'Path' as fwd decl
        pass

class Path:
    def __init__(self):
        self.commands = []

    def moveto(self, x: float, y: float):
        print(f"Move to: ({x}, {y})")

    def lineto(self, x: float, y: float):
        print(f"Draw line to: ({x}, {y})")

    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        print(f"Draw cubic Bézier curve: ({x1}, {y1}) -> ({x2}, {y2}) -> ({x3}, {y3})")

    def execute_command(self, command: PathCommand):
        command.execute(self)

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
