import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class GraphicsState:
    def __init__(self):
        self.path = []
        self.line_width = 1.0
        self.fill_color = (0, 0, 0)
        self.stroke_color = (0, 0, 0)
        self.current_position = (0, 0)
        self.saved_states = []

    def save(self):
        logging.debug("Saving state: %s", self.__dict__)
        self.saved_states.append({
            "path": list(self.path),
            "line_width": self.line_width,
            "fill_color": self.fill_color,
            "stroke_color": self.stroke_color,
            "current_position": self.current_position
        })

    def restore(self):
        if self.saved_states:
            state = self.saved_states.pop()
            logging.debug("Restoring state: %s", state)
            self.path = state["path"]
            self.line_width = state["line_width"]
            self.fill_color = state["fill_color"]
            self.stroke_color = state["stroke_color"]
            self.current_position = state["current_position"]


class Command:
    def execute(self, interpreter):
        raise NotImplementedError("Execute must be implemented by subclasses")


class NewPathCommand(Command):
    def execute(self, interpreter):
        logging.debug("Executing NewPathCommand")
        interpreter.graphics_state.path = []


class MoveToCommand(Command):
    def execute(self, interpreter):
        y, x = interpreter.pop_two()  # PostScript order (y, x)
        interpreter.graphics_state.current_position = (x, y)
        logging.debug("Moving to position: (%d, %d)", x, y)


class LineToCommand(Command):
    def execute(self, interpreter):
        y, x = interpreter.pop_two()  # PostScript order (y, x)
        start_pos = interpreter.graphics_state.current_position
        end_pos = (x, y)
        interpreter.graphics_state.path.append((start_pos, end_pos))
        interpreter.graphics_state.current_position = end_pos
        logging.debug("Drawing line from %s to %s", start_pos, end_pos)


class SetLineWidthCommand(Command):
    def execute(self, interpreter):
        line_width = interpreter.stack.pop()
        interpreter.graphics_state.line_width = line_width
        logging.debug("Setting line width to: %f", line_width)


class SetGrayCommand(Command):
    def execute(self, interpreter):
        gray = interpreter.stack.pop()
        interpreter.graphics_state.fill_color = interpreter.graphics_state.stroke_color = (gray, gray, gray)
        logging.debug("Setting grayscale color to: %f", gray)


class SetRGBColorCommand(Command):
    def execute(self, interpreter):
        b, g, r = interpreter.pop_three()  # PostScript order (b, g, r)
        interpreter.graphics_state.fill_color = interpreter.graphics_state.stroke_color = (r, g, b)
        logging.debug("Setting RGB color to: (%d, %d, %d)", r, g, b)


class StrokeCommand(Command):
    def execute(self, interpreter):
        path = interpreter.graphics_state.path
        color = interpreter.graphics_state.stroke_color
        line_width = interpreter.graphics_state.line_width
        interpreter.rasterizer.stroke(path, color, line_width)
        logging.debug("Stroke command executed with color: %s and line width: %f", color, line_width)


class FillCommand(Command):
    def execute(self, interpreter):
        path = interpreter.graphics_state.path
        color = interpreter.graphics_state.fill_color
        interpreter.rasterizer.fill(path, color)
        logging.debug("Fill command executed with color: %s", color)


class ClosePathCommand(Command):
    def execute(self, interpreter):
        if interpreter.graphics_state.path:
            start_point = interpreter.graphics_state.path[0][0]  # first segment
            current_position = interpreter.graphics_state.current_position
            interpreter.graphics_state.path.append((current_position, start_point))
            interpreter.graphics_state.current_position = start_point
            logging.debug("Closing path from %s to %s", current_position, start_point)


class Interpreter:
    def __init__(self, rasterizer):
        self.stack = []
        self.graphics_state = GraphicsState()
        self.rasterizer = rasterizer
        self.commands = {
            "newpath": NewPathCommand(),
            "moveto": MoveToCommand(),
            "lineto": LineToCommand(),
            "setlinewidth": SetLineWidthCommand(),
            "setgray": SetGrayCommand(),
            "setrgbcolor": SetRGBColorCommand(),
            "stroke": StrokeCommand(),
            "fill": FillCommand(),
            "closepath": ClosePathCommand(),
        }

    def execute(self, program):
        for token in program:
            if isinstance(token, (int, float, tuple)):  # numbers or tuples onto the stack
                self.stack.append(token)
            elif isinstance(token, str):  # exec commands
                if token in self.commands:
                    logging.debug("Executing command: %s", token)
                    self.commands[token].execute(self)
                else:
                    raise ValueError(f"Unknown command: {token}")
            else:
                raise ValueError(f"Invalid token: {token}")

    def pop_two(self):
        return self.stack.pop(), self.stack.pop()

    def pop_three(self):
        return self.stack.pop(), self.stack.pop(), self.stack.pop()


class Rasterizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.canvas = [[(1.0, 1.0, 1.0) for _ in range(width)] for _ in range(height)]

    def stroke(self, path, color, line_width):
        for segment in path:
            if segment == "close":
                continue
            self._draw_line(segment[0], segment[1], color)

    def fill(self, path, color):
        for segment in path:
            if isinstance(segment, tuple):
                self._draw_line(segment[0], segment[1], color)
        self._flood_fill(color)

    def _draw_line(self, start, end, color): # wu lines ..
        def plot(x, y, intensity):
            if 0 <= x < self.width and 0 <= y < self.height:
                r, g, b = color
                base_color = self.canvas[y][x]
                br, bg, bb = base_color
                new_color = (
                    int(r * intensity + br * (1 - intensity)),
                    int(g * intensity + bg * (1 - intensity)),
                    int(b * intensity + bb * (1 - intensity)),
                )
                self.canvas[y][x] = new_color

        def frac(x):
            return x - int(x)

        def rfpart(x):
            return 1 - frac(x)

        x1, y1 = start
        x2, y2 = end
        steep = abs(y2 - y1) > abs(x2 - x1)

        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        dx = x2 - x1
        dy = y2 - y1
        gradient = dy / dx if dx != 0 else 1

        xend = round(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = rfpart(x1 + 0.5)
        xpxl1 = xend
        ypxl1 = int(yend)
        if steep:
            plot(ypxl1, xpxl1, rfpart(yend) * xgap)
            plot(ypxl1 + 1, xpxl1, frac(yend) * xgap)
        else:
            plot(xpxl1, ypxl1, rfpart(yend) * xgap)
            plot(xpxl1, ypxl1 + 1, frac(yend) * xgap)

        intery = yend + gradient

        xend = round(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = frac(x2 + 0.5)
        xpxl2 = xend
        ypxl2 = int(yend)
        if steep:
            plot(ypxl2, xpxl2, rfpart(yend) * xgap)
            plot(ypxl2 + 1, xpxl2, frac(yend) * xgap)
        else:
            plot(xpxl2, ypxl2, rfpart(yend) * xgap)
            plot(xpxl2, ypxl2 + 1, frac(yend) * xgap)

        for x in range(xpxl1 + 1, xpxl2):
            if steep:
                plot(int(intery), x, rfpart(intery))
                plot(int(intery) + 1, x, frac(intery))
            else:
                plot(x, int(intery), rfpart(intery))
                plot(x, int(intery) + 1, frac(intery))
            intery += gradient

    def _flood_fill(self, fill_color):
        seed_x, seed_y = self.width // 2, self.height // 2
        target_color = self.canvas[seed_y][seed_x]

        if target_color == fill_color:
            return  # no infinite recursion

        stack = [(seed_x, seed_y)]
        while stack:
            x, y = stack.pop()
            if 0 <= x < self.width and 0 <= y < self.height and self.canvas[y][x] == target_color:
                self.canvas[y][x] = fill_color
                stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

    def save_to_ppm(self, filename):
        with open(filename, 'w') as f:
            f.write("P3\n")
            f.write(f"{self.width} {self.height}\n")
            f.write("255\n")
            for row in self.canvas:
                for r, g, b in row:
                    f.write(f"{int(r * 255)} {int(g * 255)} {int(b * 255)} ")
                f.write("\n")

# example
rasterizer = Rasterizer(300, 300)
interpreter = Interpreter(rasterizer)

program = [
    "newpath",
    50, 50, "moveto",
    250, 50, "lineto",
    250, 250, "lineto",
    50, 250, "lineto",
    "closepath",
    0, 0, 1, "setrgbcolor",  # blue
    "fill",
    1, 0, 0, "setrgbcolor",  # red
    2, "setlinewidth", # not impl.
    "stroke",
]

interpreter.execute(program)
rasterizer.save_to_ppm("output4.ppm")
