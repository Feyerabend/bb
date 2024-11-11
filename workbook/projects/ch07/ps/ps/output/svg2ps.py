import math

class Transform:
    def __init__(self):
        # Initialize with the identity matrix
        self.matrix = [1, 0, 0, 1, 0, 0]

    def apply_translation(self, tx, ty):
        """Apply a translation transformation"""
        self.matrix[4] += tx * self.matrix[0] + ty * self.matrix[2]
        self.matrix[5] += tx * self.matrix[1] + ty * self.matrix[3]

    def apply_scaling(self, sx, sy):
        """Apply a scaling transformation"""
        self.matrix[0] *= sx
        self.matrix[1] *= sx
        self.matrix[2] *= sy
        self.matrix[3] *= sy

    def apply_rotation(self, angle):
        """Apply a rotation transformation"""
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        m0, m1, m2, m3 = self.matrix[0], self.matrix[1], self.matrix[2], self.matrix[3]
        self.matrix[0] = m0 * cos_a + m2 * sin_a
        self.matrix[1] = m1 * cos_a + m3 * sin_a
        self.matrix[2] = m0 * -sin_a + m2 * cos_a
        self.matrix[3] = m1 * -sin_a + m3 * cos_a

    def apply_transform(self, x, y):
        """Apply the current transformation matrix to a point"""
        new_x = x * self.matrix[0] + y * self.matrix[2] + self.matrix[4]
        new_y = x * self.matrix[1] + y * self.matrix[3] + self.matrix[5]
        return new_x, new_y

    def to_postscript(self):
        """Convert to PostScript transformation syntax"""
        return f"{self.matrix[0]} {self.matrix[1]} {self.matrix[2]} {self.matrix[3]} {self.matrix[4]} {self.matrix[5]} concat"


class SVGtoPostScriptConverter:
    def __init__(self):
        self.transform_stack = [Transform()]

    def apply_transform(self, transform_str):
        """Parse and apply SVG transform commands"""
        transform = self.transform_stack[-1]  # Work on the current transform
        commands = transform_str.split(')')  # Split by each transform type

        for command in commands:
            if 'translate' in command:
                tx, ty = map(float, command[command.index('(') + 1:].split(','))
                transform.apply_translation(tx, ty)
            elif 'scale' in command:
                sx, sy = map(float, command[command.index('(') + 1:].split(','))
                transform.apply_scaling(sx, sy)
            elif 'rotate' in command:
                angle = float(command[command.index('(') + 1:].strip())
                transform.apply_rotation(angle)

    def convert_circle(self, cx, cy, r):
        """Convert an SVG circle to PostScript format with transformations applied"""
        transformed_center = self.transform_stack[-1].apply_transform(cx, cy)
        ps_commands = [
            f"newpath",
            f"{transformed_center[0]} {transformed_center[1]} {r} 0 360 arc",
            f"stroke"
        ]
        return "\n".join(ps_commands)

    def convert_rect(self, x, y, width, height):
        """Convert an SVG rectangle to PostScript format with transformations applied"""
        transformed_start = self.transform_stack[-1].apply_transform(x, y)
        ps_commands = [
            f"newpath",
            f"{transformed_start[0]} {transformed_start[1]} moveto",
            f"{width} 0 rlineto",
            f"0 {height} rlineto",
            f"{-width} 0 rlineto",
            f"closepath",
            f"stroke"
        ]
        return "\n".join(ps_commands)

    def begin_transform(self, transform_str):
        """Start a new transformation context with a given SVG transform string"""
        new_transform = Transform()
        self.transform_stack.append(new_transform)
        self.apply_transform(transform_str)

    def end_transform(self):
        """End the current transformation context"""
        if len(self.transform_stack) > 1:
            self.transform_stack.pop()

    def convert_svg_to_ps(self, svg_commands):
        """Convert a list of SVG commands to PostScript, handling transforms"""
        ps_output = []
        for command in svg_commands:
            if command['type'] == 'circle':
                ps_output.append(self.convert_circle(command['cx'], command['cy'], command['r']))
            elif command['type'] == 'rect':
                ps_output.append(self.convert_rect(command['x'], command['y'], command['width'], command['height']))
            elif command['type'] == 'transform_start':
                self.begin_transform(command['transform'])
            elif command['type'] == 'transform_end':
                self.end_transform()
        return "\n".join(ps_output)

# Example SVG input (hypothetical)
svg_commands = [
    {'type': 'transform_start', 'transform': 'translate(100,100) scale(2,2)'},
    {'type': 'circle', 'cx': 0, 'cy': 0, 'r': 50},
    {'type': 'transform_end'},
    {'type': 'rect', 'x': 150, 'y': 150, 'width': 100, 'height': 100},
]

# Convert and print PostScript output
converter = SVGtoPostScriptConverter()
ps_output = converter.convert_svg_to_ps(svg_commands)
print(ps_output)
