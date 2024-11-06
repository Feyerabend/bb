class Path:
    def __init__(self):
        pass

    def moveto(self, x: float, y: float):
        pass

    def lineto(self, x: float, y: float):
        pass

    # PostScript primarily uses cubic Bézier curves to define shapes and paths.
    # These curves are parametrized by four points: two endpoints and two control points
    # two points come from moveto ..?
    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        pass

    def closepath(self):
        pass