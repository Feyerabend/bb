import math

class GeometryUtils:
    @staticmethod
    def distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    @staticmethod
    def point_on_line(x0: float, y0: float, x1: float, y1: float, t: float) -> tuple[float, float]:
        x = x0 + t * (x1 - x0)
        y = y0 + t * (y1 - y0)
        return x, y