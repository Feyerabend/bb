class GraphicsState:
    def __init__(self):
        pass

    def set_color(self, r: int, g: int, b: int):
        pass

    def set_line_width(self, width: float):
        pass

    def apply_transform(self, matrix: list[list[float]]):
        pass

    def push_state(self):
        pass

    def pop_state(self):
        pass