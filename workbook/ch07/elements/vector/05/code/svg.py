import xml.etree.ElementTree as ET
import re
from pathlib import Path as FilePath
import math
from typing import Tuple, List, Dict, Any, Optional

from render import Path, AntiAliasedRasterizer
from render import StrokeProperties, FillProperties
from render import EvenOddFillRule, NonZeroWindingFillRule
from render import save_to_png, LineCap, LineJoin

DEBUG = True

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

class SVGParser:

    SVG_NS = "{http://www.w3.org/2000/svg}"

    def __init__(self):
        self.paths = []
        self.width = 0
        self.height = 0
        self.view_box = None
        self.preserve_aspect_ratio = 'xMidYMid meet'


    def parse_file(self, svg_path: str) -> None:
        debug_print(f"\n=== Parsing SVG File: {svg_path} ===")
        tree = ET.parse(svg_path)
        root = tree.getroot()  # This is the actual XML root element
        
        # Pass the root ELEMENT to dimensions parser
        self._parse_dimensions(root)
        self._process_element(root, {}, None)
        debug_print(f"Parsed {len(self.paths)} paths") 

       
        self.width = self._parse_dimensions(root.get('width', '0'))
        self.height = self._parse_dimensions(root.get('height', '0'))
        debug_print(f"SVG dimensions: width={self.width}, height={self.height}")
        
        view_box_str = root.get('viewBox')
        if view_box_str:
            self.view_box = [float(x) for x in view_box_str.split()]
            debug_print(f"ViewBox: {self.view_box}")
        
        self.preserve_aspect_ratio = root.get('preserveAspectRatio', 'xMidYMid meet')
        debug_print(f"PreserveAspectRatio: {self.preserve_aspect_ratio}")
        
        self._process_element(root, parent_style={}, parent_transform=None)

    def _parse_dimensions(self, root: ET.Element) -> None:
        self.original_width = self._parse_unit(root.get('width', '0'))
        self.original_height = self._parse_unit(root.get('height', '0'))
        debug_print(f"Original dimensions: {self.original_width}x{self.original_height}")

        if view_box := root.get('viewBox'):
            self.view_box = list(map(float, view_box.split()))
            debug_print(f"ViewBox found: {self.view_box}")
            
            # Use viewBox dimensions if original dimensions are invalid
            if self.original_width <= 0 and len(self.view_box) >= 4:
                self.original_width = self.view_box[2]
            if self.original_height <= 0 and len(self.view_box) >= 4:
                self.original_height = self.view_box[3]

        self.preserve_aspect_ratio = root.get('preserveAspectRatio', 'xMidYMid meet')
        debug_print(f"Final content dimensions: {self.original_width}x{self.original_height}")
        debug_print(f"Aspect ratio handling: {self.preserve_aspect_ratio}")

    def _parse_unit(self, value: str) -> float:
        debug_print(f"Parsing unit: {value}")
        match = re.match(r"^([+-]?\d*\.?\d+)(%|px|pt|pc|cm|mm|in|em|ex)?$", value.strip())
        if not match:
            return 0.0
            
        num, unit = match.groups()
        conversions = {
            None: 1,     # Default to pixels
            'px': 1,
            'pt': 1.3333, 'pc': 16,     # 1pt=1.333px, 1pc=16px
            'cm': 37.795, 'mm': 3.7795,  # 1cm=37.795px, 1mm=3.7795px
            'in': 96,                    # 1in=96px
            'em': 16, 'ex': 8            # Typical defaults
        }
        return float(num) * conversions.get(unit, 1)

    def _parse_transform(self, transform_str: str) -> Optional[List[float]]:
        if not transform_str:
            return None
        matrix = [1, 0, 0, 1, 0, 0]
        for transform in re.finditer(r'(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]+)\)', transform_str):
            name, args = transform.groups()
            args = [float(x) for x in re.split(r'[\s,]+', args.strip())]
            if name == 'matrix' and len(args) == 6:
                matrix = self._multiply_matrices(matrix, args)
            elif name == 'translate' and len(args) in (1, 2):
                tx, ty = args[0], args[1] if len(args) == 2 else 0
                matrix = self._multiply_matrices(matrix, [1, 0, 0, 1, tx, ty])
            elif name == 'scale' and len(args) in (1, 2):
                sx, sy = args[0], args[1] if len(args) == 2 else args[0]
                matrix = self._multiply_matrices(matrix, [sx, 0, 0, sy, 0, 0])
            elif name == 'rotate' and len(args) in (1, 3):
                angle = math.radians(args[0])
                if len(args) == 3:
                    cx, cy = args[1], args[2]
                    matrix = self._multiply_matrices(matrix, [1, 0, 0, 1, cx, cy])
                    matrix = self._multiply_matrices(matrix, [
                        math.cos(angle), math.sin(angle),
                        -math.sin(angle), math.cos(angle), 0, 0
                    ])
                    matrix = self._multiply_matrices(matrix, [1, 0, 0, 1, -cx, -cy])
                else:
                    matrix = self._multiply_matrices(matrix, [
                        math.cos(angle), math.sin(angle),
                        -math.sin(angle), math.cos(angle), 0, 0
                    ])
            elif name == 'skewX' and len(args) == 1:
                matrix = self._multiply_matrices(matrix, [
                    1, 0, math.tan(math.radians(args[0])), 1, 0, 0
                ])
            elif name == 'skewY' and len(args) == 1:
                matrix = self._multiply_matrices(matrix, [
                    1, math.tan(math.radians(args[0])), 0, 1, 0, 0
                ])
        return matrix

    def _multiply_matrices(self, m1: List[float], m2: List[float]) -> List[float]:
        a1, b1, c1, d1, e1, f1 = m1
        a2, b2, c2, d2, e2, f2 = m2
        return [
            a1*a2 + c1*b2, b1*a2 + d1*b2,
            a1*c2 + c1*d2, b1*c2 + d1*d2,
            a1*e2 + c1*f2 + e1, b1*e2 + d1*f2 + f1
        ]

    def _process_element(self, element: ET.Element, parent_style: Dict[str, str], parent_transform: Optional[List[float]]) -> None:
        tag_name = element.tag.split('}', 1)[-1]
        current_style = parent_style.copy()

        # Process presentation attributes first
        for key in ['stroke', 'stroke-width', 'stroke-opacity', 'stroke-linecap',
                   'stroke-linejoin', 'fill', 'fill-opacity', 'fill-rule', 
                   'miter-limit', 'color']:
            if key in element.attrib:
                current_style[key] = element.get(key)

        # Then process style attribute
        if style_str := element.get('style', ''):
            for item in style_str.split(';'):
                if ':' in item:
                    key, value = item.split(':', 1)
                    current_style[key.strip()] = value.strip()

        # Process transform
        transform_str = element.get('transform', '')
        current_transform = self._parse_transform(transform_str)
        if parent_transform and current_transform:
            current_transform = self._multiply_matrices(parent_transform, current_transform)
        elif parent_transform:
            current_transform = parent_transform.copy()

        # Process elements
        if tag_name == 'path':
            self._process_path(element, current_style, current_transform)
        elif tag_name == 'rect':
            self._process_rect(element, current_style, current_transform)
        elif tag_name in ['circle', 'ellipse', 'line', 'polyline', 'polygon']:
            getattr(self, f'_process_{tag_name}')(element, current_style, current_transform)
        elif tag_name == 'g':
            for child in element:
                self._process_element(child, current_style, current_transform)
        elif tag_name == 'svg':
            # Handle nested SVGs
            for child in element:
                self._process_element(child, current_style, current_transform)
        else:
            debug_print(f"Unknown SVG element: {tag_name}, skipping")
        debug_print(f"Processed element: {tag_name}, current style: {current_style}")

    def _process_path(self, element: ET.Element, style: Dict[str, str], transform: List[float]) -> None:
        if not (d := element.get('d', '')):
            return
        path = Path()
        try:
            self._parse_path_data(path, d)
            if path.elements and 'fill' in style and style['fill'] != 'none':
                if path.current_point and path.elements[0].start.is_close(path.current_point):
                    path.close()
        except ValueError:
            return
        
        stroke_props, fill_props = self._get_style_properties(element, style)
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
        debug_print(f"Added path to paths list, total paths: {len(self.paths)}")


    def _parse_path_data(self, path: Path, d: str) -> None:
        d = re.sub(r',', ' ', d).strip()
        tokens = re.findall(r'[A-Za-z]|-?\d*\.?\d+(?:[eE][-+]?\d+)?', d)
        i = 0
        current_x, current_y = 0.0, 0.0
        start_x, start_y = 0.0, 0.0
        last_control_x, last_control_y = None, None
        command = None

        def parse_numbers(count):
            nonlocal i
            numbers = []
            while len(numbers) < count and i < len(tokens):
                if tokens[i].isdigit() or '.' in tokens[i] or tokens[i] in ('-', '+'):
                    numbers.append(float(tokens[i]))
                    i += 1
                else:
                    break
            return numbers

        while i < len(tokens):
            if tokens[i].isalpha():
                command = tokens[i]
                i += 1
            else:
                # Implicit command (same as previous)
                if command is None:
                    raise ValueError("Missing initial command in path data")
                
            cmd = command.upper()
            relative = command.islower() # flag instead of using 'a' or 'A
            numbers = []

            if cmd in ('M', 'L', 'T'):
                numbers_needed = 2
            elif cmd in ('H', 'V'):
                numbers_needed = 1
            elif cmd in ('S', 'Q'):
                numbers_needed = 4
            elif cmd == 'C':
                numbers_needed = 6
            elif cmd == 'A':
                numbers_needed = 7
            elif cmd == 'Z':
                numbers_needed = 0
            else:
                raise ValueError(f"Unknown command: {cmd}")

            while True:
                numbers = parse_numbers(numbers_needed)
                if len(numbers) < numbers_needed:
                    break

                if cmd == 'M':  # Move-to
                    x, y = numbers[0], numbers[1]
                    if relative:
                        x += current_x
                        y += current_y
                    path.move_to(x, y)
                    current_x, current_y = x, y
                    start_x, start_y = x, y
                    # Subsequent pairs are implicit line-tos
                    cmd = 'L' if cmd == 'M' else 'l'

                elif cmd == 'L':  # Line-to
                    x, y = numbers[0], numbers[1]
                    if relative:
                        x += current_x
                        y += current_y
                    path.line_to(x, y)
                    current_x, current_y = x, y

                elif cmd == 'H':  # Horizontal line-to
                    x = numbers[0]
                    if relative:
                        x += current_x
                    path.line_to(x, current_y)
                    current_x = x

                elif cmd == 'V':  # Vertical line-to
                    y = numbers[0]
                    if relative:
                        y += current_y
                    path.line_to(current_x, y)
                    current_y = y

                elif cmd == 'C':  # Cubic Bézier
                    x1, y1, x2, y2, x, y = numbers
                    if relative:
                        x1 += current_x
                        y1 += current_y
                        x2 += current_x
                        y2 += current_y
                        x += current_x
                        y += current_y
                    path.cubic_bezier_to(x1, y1, x2, y2, x, y)
                    last_control_x, last_control_y = x2, y2
                    current_x, current_y = x, y

                elif cmd == 'S':  # Smooth cubic Bézier
                    x2, y2, x, y = numbers
                    if relative:
                        x2 += current_x
                        y2 += current_y
                        x += current_x
                        y += current_y
                    # Reflect previous control point
                    x1 = 2 * current_x - last_control_x if last_control_x else current_x
                    y1 = 2 * current_y - last_control_y if last_control_y else current_y
                    path.cubic_bezier_to(x1, y1, x2, y2, x, y)
                    last_control_x, last_control_y = x2, y2
                    current_x, current_y = x, y

                elif cmd == 'Q':  # Quadratic Bézier
                    x1, y1, x, y = numbers
                    if relative:
                        x1 += current_x
                        y1 += current_y
                        x += current_x
                        y += current_y
                    # Convert to cubic Bézier
                    cp1x = current_x + (2/3) * (x1 - current_x)
                    cp1y = current_y + (2/3) * (y1 - current_y)
                    cp2x = x + (2/3) * (x1 - x)
                    cp2y = y + (2/3) * (y1 - y)
                    path.cubic_bezier_to(cp1x, cp1y, cp2x, cp2y, x, y)
                    last_control_x, last_control_y = x1, y1
                    current_x, current_y = x, y

                elif cmd == 'T':  # Smooth quadratic Bézier
                    x, y = numbers
                    if relative:
                        x += current_x
                        y += current_y
                    # Reflect previous control point
                    x1 = 2 * current_x - last_control_x if last_control_x else current_x
                    y1 = 2 * current_y - last_control_y if last_control_y else current_y
                    # Convert to cubic Bézier
                    cp1x = current_x + (2/3) * (x1 - current_x)
                    cp1y = current_y + (2/3) * (y1 - current_y)
                    cp2x = x + (2/3) * (x1 - x)
                    cp2y = y + (2/3) * (y1 - y)
                    path.cubic_bezier_to(cp1x, cp1y, cp2x, cp2y, x, y)
                    last_control_x, last_control_y = x1, y1
                    current_x, current_y = x, y

                elif cmd == 'A':  # Elliptical arc
                    rx, ry, x_rot, large_arc, sweep, x, y = numbers
                    if relative:
                        x += current_x
                        y += current_y
                    if rx == 0 or ry == 0:
                        path.line_to(x, y)
                        current_x, current_y = x, y
                        continue
                    
                    # Convert arc to cubic Béziers
                    curves = self._arc_to_bezier(current_x, current_y, rx, ry, x_rot, 
                                            large_arc, sweep, x, y)
                    for j in range(0, len(curves), 6):
                        x1, y1, x2, y2, ex, ey = curves[j:j+6]
                        path.cubic_bezier_to(x1, y1, x2, y2, ex, ey)
                        last_control_x, last_control_y = x2, y2
                    current_x, current_y = x, y

                elif cmd == 'Z':  # Close path
                    path.close()
                    current_x, current_y = start_x, start_y
                    last_control_x = last_control_y = None

                numbers = []
            
            # After processing command, reset control point if needed
            if cmd in ('L', 'H', 'V', 'Z'):
                last_control_x = last_control_y = None

    def _arc_to_bezier(self, x1: float, y1: float, rx: float, ry: float, phi: float, large_arc: int, sweep: int, x2: float, y2: float) -> List[float]:
        debug_print(f"Converting arc: ({x1}, {y1}) to ({x2}, {y2}), rx={rx}, ry={ry}, phi={phi}, large_arc={large_arc}, sweep={sweep}")
        if x1 == x2 and y1 == y2 or rx == 0 or ry == 0:
            debug_print("Invalid arc parameters, returning empty list")
            return []
        rx, ry = abs(rx), abs(ry)
        phi = math.radians(phi)
        cos_phi, sin_phi = math.cos(phi), math.sin(phi)
        dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
        x1p = cos_phi * dx + sin_phi * dy
        y1p = -sin_phi * dx + cos_phi * dy
        lambda_val = (x1p / rx) ** 2 + (y1p / ry) ** 2
        if lambda_val > 1:
            rx *= math.sqrt(lambda_val)
            ry *= math.sqrt(lambda_val)
            debug_print(f"Adjusted arc radii: rx={rx}, ry={ry}")
        sign = -1 if large_arc == sweep else 1
        sq = max(0, (rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2) / (rx**2 * y1p**2 + ry**2 * x1p**2))
        coef = sign * math.sqrt(sq)
        cxp = coef * rx * y1p / ry
        cyp = -coef * ry * x1p / rx
        cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2
        cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2
        theta1 = math.atan2((y1p - cyp) / ry, (x1p - cxp) / rx)
        delta_theta = math.atan2((-y1p - cyp) / ry, (-x1p - cxp) / rx) - theta1
        if sweep == 0 and delta_theta > 0:
            delta_theta -= 2 * math.pi
        elif sweep == 1 and delta_theta < 0:
            delta_theta += 2 * math.pi
        segments = max(1, int(abs(delta_theta) / (math.pi / 2)) + 1)
        delta_theta /= segments
        result = []
        kappa = 4 / 3 * math.tan(delta_theta / 4)
        theta = theta1
        for _ in range(segments):
            cos_theta, sin_theta = math.cos(theta), math.sin(theta)
            cos_theta1, sin_theta1 = math.cos(theta + delta_theta), math.sin(theta + delta_theta)
            p0x = cx + rx * cos_theta * cos_phi - ry * sin_theta * sin_phi
            p0y = cy + rx * cos_theta * sin_phi + ry * sin_theta * cos_phi
            p1x = p0x - kappa * (rx * sin_theta * cos_phi + ry * cos_theta * sin_phi)
            p1y = p0y - kappa * (rx * sin_theta * sin_phi - ry * cos_theta * cos_phi)
            p3x = cx + rx * cos_theta1 * cos_phi - ry * sin_theta1 * sin_phi
            p3y = cy + rx * cos_theta1 * sin_phi + ry * sin_theta1 * cos_phi
            p2x = p3x + kappa * (rx * sin_theta1 * cos_phi + ry * cos_theta1 * sin_phi)
            p2y = p3y + kappa * (rx * sin_theta1 * sin_phi - ry * cos_theta1 * cos_phi)
            result.extend([p1x, p1y, p2x, p2y, p3x, p3y])
            theta += delta_theta
        debug_print(f"Arc converted to {len(result)//6} Bézier curves")
        return result

    def _process_rect(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        x = float(element.get('x', '0'))
        y = float(element.get('y', '0'))
        width = float(element.get('width', '0'))
        height = float(element.get('height', '0'))
        rx = float(element.get('rx', '0'))
        ry = float(element.get('ry', '0'))
        debug_print(f"Processing rect: x={x}, y={y}, width={width}, height={height}, rx={rx}, ry={ry}")
        path = Path()
        if rx <= 0 and ry <= 0:
            path.move_to(x, y)
            path.line_to(x + width, y)
            path.line_to(x + width, y + height)
            path.line_to(x, y + height)
            path.close()
        else:
            if rx <= 0:
                rx = ry
            if ry <= 0:
                ry = rx
            rx = min(rx, width / 2)
            ry = min(ry, height / 2)
            path.move_to(x + rx, y)
            path.line_to(x + width - rx, y)
            path.cubic_bezier_to(x + width, y, x + width, y, x + width, y + ry)
            path.line_to(x + width, y + height - ry)
            path.cubic_bezier_to(x + width, y + height, x + width, y + height, x + width - rx, y + height)
            path.line_to(x + rx, y + height)
            path.cubic_bezier_to(x, y + height, x, y + height, x, y + height - ry)
            path.line_to(x, y + ry)
            path.cubic_bezier_to(x, y, x, y, x + rx, y)
            path.close()
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        debug_print(f"Rect styles - Stroke: {stroke_props}, Fill: {fill_props}")
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
        debug_print(f"Added rect path to paths list, total paths: {len(self.paths)}")

    def _process_circle(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        cx = float(element.get('cx', '0'))
        cy = float(element.get('cy', '0'))
        r = float(element.get('r', '0'))
        debug_print(f"Processing circle: cx={cx}, cy={cy}, r={r}")
        path = Path()
        kappa = 0.5522848
        path.move_to(cx + r, cy)
        path.cubic_bezier_to(cx + r, cy - kappa * r, cx + kappa * r, cy - r, cx, cy - r)
        path.cubic_bezier_to(cx - kappa * r, cy - r, cx - r, cy - kappa * r, cx - r, cy)
        path.cubic_bezier_to(cx - r, cy + kappa * r, cx - kappa * r, cy + r, cx, cy + r)
        path.cubic_bezier_to(cx + kappa * r, cy + r, cx + r, cy + kappa * r, cx + r, cy)
        path.close()
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        debug_print(f"Circle styles - Stroke: {stroke_props}, Fill: {fill_props}")
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
        debug_print(f"Added circle path to paths list, total paths: {len(self.paths)}")

    def _process_ellipse(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        cx = float(element.get('cx', '0'))
        cy = float(element.get('cy', '0'))
        rx = float(element.get('rx', '0'))
        ry = float(element.get('ry', '0'))
        debug_print(f"Processing ellipse: cx={cx}, cy={cy}, rx={rx}, ry={ry}")
        path = Path()
        kappa = 0.5522848
        path.move_to(cx + rx, cy)
        path.cubic_bezier_to(cx + rx, cy - kappa * ry, cx + kappa * rx, cy - ry, cx, cy - ry)
        path.cubic_bezier_to(cx - kappa * rx, cy - ry, cx - rx, cy - kappa * ry, cx - rx, cy)
        path.cubic_bezier_to(cx - rx, cy + kappa * ry, cx - kappa * rx, cy + ry, cx, cy + ry)
        path.cubic_bezier_to(cx + kappa * rx, cy + ry, cx + rx, cy + kappa * ry, cx + rx, cy)
        path.close()
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        debug_print(f"Ellipse styles - Stroke: {stroke_props}, Fill: {fill_props}")
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
        debug_print(f"Added ellipse path to paths list, total paths: {len(self.paths)}")

    def _process_line(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        x1 = float(element.get('x1', '0'))
        y1 = float(element.get('y1', '0'))
        x2 = float(element.get('x2', '0'))
        y2 = float(element.get('y2', '0'))
        debug_print(f"Processing line: from ({x1}, {y1}) to ({x2}, {y2})")
        path = Path()
        path.move_to(x1, y1)
        path.line_to(x2, y2)
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        debug_print(f"Line styles - Stroke: {stroke_props}, Fill: {fill_props}")
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': None,
            'transform': transform
        })
        debug_print(f"Added line path to paths list, total paths: {len(self.paths)}")

    def _process_polyline(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        points_str = element.get('points', '')
        debug_print(f"Processing polyline: points={points_str[:50]}{'...' if len(points_str) > 50 else ''}")
        if not points_str:
            debug_print("Empty polyline points, skipping")
            return
        points = []
        for point in re.finditer(r'([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+))\s*,?\s*([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+))', points_str):
            points.append((float(point.group(1)), float(point.group(2))))
        if not points:
            debug_print("No valid points found in polyline, skipping")
            return
        path = Path()
        path.move_to(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.line_to(x, y)
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        debug_print(f"Polyline styles - Stroke: {stroke_props}, Fill: {fill_props}")
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': None,
            'transform': transform
        })
        debug_print(f"Added polyline path to paths list, total paths: {len(self.paths)}")

    def _process_polygon(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        points_str = element.get('points', '')
        debug_print(f"Processing polygon: points={points_str[:50]}{'...' if len(points_str) > 50 else ''}")
        if not points_str:
            debug_print("Empty polygon points, skipping")
            return
        points = []
        for point in re.finditer(r'([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+))\s*,?\s*([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+))', points_str):
            points.append((float(point.group(1)), float(point.group(2))))
        if not points:
            debug_print("No valid points found in polygon, skipping")
            return
        path = Path()
        path.move_to(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.line_to(x, y)
        path.close()
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        debug_print(f"Polygon styles - Stroke: {stroke_props}, Fill: {fill_props}")
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
        debug_print(f"Added polygon path to paths list, total paths: {len(self.paths)}")

    def _get_style_properties(self, element: ET.Element, style: Dict[str, str]) -> Tuple[Optional[StrokeProperties], Optional[FillProperties]]:
        stroke_props = None
        if style.get('stroke', 'none') != 'none':
            color = self._parse_color(style.get('stroke', 'black'), style)
            width = float(style.get('stroke-width', 1))
            opacity = float(style.get('stroke-opacity', 1))
            linecap = LineCap[style.get('stroke-linecap', 'butt').upper()]
            linejoin = LineJoin[style.get('stroke-linejoin', 'miter').upper()]
            miter_limit = float(style.get('miter-limit', 4))
            stroke_props = StrokeProperties(
                color=(*color[:3], int(color[3] * opacity)),
                width=width,
                line_cap=linecap,
                line_join=linejoin,
                miter_limit=miter_limit
            )

        fill_props = None
        if style.get('fill', 'none') != 'none':
            color = self._parse_color(style.get('fill', 'black'), style)
            opacity = float(style.get('fill-opacity', 1))
            rule = EvenOddFillRule() if style.get('fill-rule') == 'evenodd' else NonZeroWindingFillRule()
            fill_props = FillProperties(
                color=(*color[:3], int(color[3] * opacity)),
                rule=rule
            )

        return stroke_props, fill_props

    def _parse_color(self, color_str: str, style: Dict[str, str]) -> Tuple[int, int, int, int]:
        debug_print(f"Parsing color: {color_str}")
        color_str = color_str.strip().lower()
        
        # Handle currentColor inheritance
        if color_str == 'currentcolor':
            inherited_color = style.get('color', 'black')
            debug_print(f"Using inherited color: {inherited_color}")
            return self._parse_color(inherited_color, style)
        
        # Transparent shortcut (rgba(0,0,0,0))
        if color_str == 'transparent':
            return (0, 0, 0, 0)
        
        # Named colors (full SVG 1.1 list)
        named_colors = {
            'aliceblue': (240, 248, 255), 'antiquewhite': (250, 235, 215),
            'aqua': (0, 255, 255), 'aquamarine': (127, 255, 212),
            'azure': (240, 255, 255), 'beige': (245, 245, 220),
            'bisque': (255, 228, 196), 'black': (0, 0, 0),
            'blanchedalmond': (255, 235, 205), 'blue': (0, 0, 255),
            'blueviolet': (138, 43, 226), 'brown': (165, 42, 42),
            'burlywood': (222, 184, 135), 'cadetblue': (95, 158, 160),
            'chartreuse': (127, 255, 0), 'chocolate': (210, 105, 30),
            'coral': (255, 127, 80), 'cornflowerblue': (100, 149, 237),
            'cornsilk': (255, 248, 220), 'crimson': (220, 20, 60),
            'cyan': (0, 255, 255), 'darkblue': (0, 0, 139),
            'darkcyan': (0, 139, 139), 'darkgoldenrod': (184, 134, 11),
            'darkgray': (169, 169, 169), 'darkgreen': (0, 100, 0),
            'darkgrey': (169, 169, 169), 'darkkhaki': (189, 183, 107),
            'darkmagenta': (139, 0, 139), 'darkolivegreen': (85, 107, 47),
            'darkorange': (255, 140, 0), 'darkorchid': (153, 50, 204),
            'darkred': (139, 0, 0), 'darksalmon': (233, 150, 122),
            'darkseagreen': (143, 188, 143), 'darkslateblue': (72, 61, 139),
            'darkslategray': (47, 79, 79), 'darkslategrey': (47, 79, 79),
            'darkturquoise': (0, 206, 209), 'darkviolet': (148, 0, 211),
            'deeppink': (255, 20, 147), 'deepskyblue': (0, 191, 255),
            'dimgray': (105, 105, 105), 'dimgrey': (105, 105, 105),
            'dodgerblue': (30, 144, 255), 'firebrick': (178, 34, 34),
            'floralwhite': (255, 250, 240), 'forestgreen': (34, 139, 34),
            'fuchsia': (255, 0, 255), 'gainsboro': (220, 220, 220),
            'ghostwhite': (248, 248, 255), 'gold': (255, 215, 0),
            'goldenrod': (218, 165, 32), 'gray': (128, 128, 128),
            'green': (0, 128, 0), 'greenyellow': (173, 255, 47),
            'grey': (128, 128, 128), 'honeydew': (240, 255, 240),
            'hotpink': (255, 105, 180), 'indianred': (205, 92, 92),
            'indigo': (75, 0, 130), 'ivory': (255, 255, 240),
            'khaki': (240, 230, 140), 'lavender': (230, 230, 250),
            'lavenderblush': (255, 240, 245), 'lawngreen': (124, 252, 0),
            'lemonchiffon': (255, 250, 205), 'lightblue': (173, 216, 230),
            'lightcoral': (240, 128, 128), 'lightcyan': (224, 255, 255),
            'lightgoldenrodyellow': (250, 250, 210), 'lightgray': (211, 211, 211),
            'lightgreen': (144, 238, 144), 'lightgrey': (211, 211, 211),
            'lightpink': (255, 182, 193), 'lightsalmon': (255, 160, 122),
            'lightseagreen': (32, 178, 170), 'lightskyblue': (135, 206, 250),
            'lightslategray': (119, 136, 153), 'lightslategrey': (119, 136, 153),
            'lightsteelblue': (176, 196, 222), 'lightyellow': (255, 255, 224),
            'lime': (0, 255, 0), 'limegreen': (50, 205, 50),
            'linen': (250, 240, 230), 'magenta': (255, 0, 255),
            'maroon': (128, 0, 0), 'mediumaquamarine': (102, 205, 170),
            'mediumblue': (0, 0, 205), 'mediumorchid': (186, 85, 211),
            'mediumpurple': (147, 112, 219), 'mediumseagreen': (60, 179, 113),
            'mediumslateblue': (123, 104, 238), 'mediumspringgreen': (0, 250, 154),
            'mediumturquoise': (72, 209, 204), 'mediumvioletred': (199, 21, 133),
            'midnightblue': (25, 25, 112), 'mintcream': (245, 255, 250),
            'mistyrose': (255, 228, 225), 'moccasin': (255, 228, 181),
            'navajowhite': (255, 222, 173), 'navy': (0, 0, 128),
            'oldlace': (253, 245, 230), 'olive': (128, 128, 0),
            'olivedrab': (107, 142, 35), 'orange': (255, 165, 0),
            'orangered': (255, 69, 0), 'orchid': (218, 112, 214),
            'palegoldenrod': (238, 232, 170), 'palegreen': (152, 251, 152),
            'paleturquoise': (175, 238, 238), 'palevioletred': (219, 112, 147),
            'papayawhip': (255, 239, 213), 'peachpuff': (255, 218, 185),
            'peru': (205, 133, 63), 'pink': (255, 192, 203),
            'plum': (221, 160, 221), 'powderblue': (176, 224, 230),
            'purple': (128, 0, 128), 'rebeccapurple': (102, 51, 153),
            'red': (255, 0, 0), 'rosybrown': (188, 143, 143),
            'royalblue': (65, 105, 225), 'saddlebrown': (139, 69, 19),
            'salmon': (250, 128, 114), 'sandybrown': (244, 164, 96),
            'seagreen': (46, 139, 87), 'seashell': (255, 245, 238),
            'sienna': (160, 82, 45), 'silver': (192, 192, 192),
            'skyblue': (135, 206, 235), 'slateblue': (106, 90, 205),
            'slategray': (112, 128, 144), 'slategrey': (112, 128, 144),
            'snow': (255, 250, 250), 'springgreen': (0, 255, 127),
            'steelblue': (70, 130, 180), 'tan': (210, 180, 140),
            'teal': (0, 128, 128), 'thistle': (216, 191, 216),
            'tomato': (255, 99, 71), 'turquoise': (64, 224, 208),
            'violet': (238, 130, 238), 'wheat': (245, 222, 179),
            'white': (255, 255, 255), 'whitesmoke': (245, 245, 245),
            'yellow': (255, 255, 0), 'yellowgreen': (154, 205, 50)
        }
        
        if color_str in named_colors:
            r, g, b = named_colors[color_str]
            return (r, g, b, 255)
        
        # Hex colors (#rgb, #rgba, #rrggbb, #rrggbbaa)
        hex_match = re.match(r'^#([a-f0-9]{3,8})$', color_str, re.IGNORECASE)
        if hex_match:
            digits = hex_match.group(1)
            length = len(digits)
            if length in (3, 4):
                return tuple(int(c * 2, 16) for c in digits[:3]) + (int(digits[3], 16) * 17,) if length == 4 else (255,)
            elif length in (6, 8):
                return (
                    int(digits[0:2], 16),
                    int(digits[2:4], 16),
                    int(digits[4:6], 16),
                    int(digits[6:8], 16) if length == 8 else 255
                )
        
        # Functional syntax (rgb/rgba/hsl/hsla)
        func_match = re.match(
            r'^(rgba?|hsla?)\(\s*([^)]+)\s*\)$',
            color_str,
            re.IGNORECASE
        )
        if func_match:
            func_type, args = func_match.groups()
            components = [x.strip() for x in re.split(r'[\s,]+', args)]
            
            if func_type.lower() in ('rgb', 'rgba'):
                # Handle percentage and decimal values
                rgb = []
                alpha = 255
                for i, c in enumerate(components[:3]):
                    if '%' in c:
                        rgb.append(min(max(round(float(c[:-1]) * 2.55), 0), 255))
                    else:
                        rgb.append(min(max(int(float(c)), 0), 255))
                
                if len(components) > 3:  # Alpha channel
                    alpha = min(max(round(float(components[3]) * 255), 0), 255)
                
                return (*rgb, alpha)
            
            elif func_type.lower() in ('hsl', 'hsla'):
                h = float(components[0].replace('deg', '').replace('rad', ''))
                s = float(components[1].strip('%')) / 100
                l = float(components[2].strip('%')) / 100
                alpha = 255 if len(components) < 4 else min(max(round(float(components[3]) * 255), 0), 255)
                
                # Convert HSL to RGB
                r, g, b = self._hsl_to_rgb(h, s, l)
                return (r, g, b, alpha)
        
        # Default to black if unrecognized format
        debug_print(f"Unknown color format: {color_str}, using black")
        return (0, 0, 0, 255)

    def _hsl_to_rgb(self, h: float, s: float, l: float) -> Tuple[int, int, int]:
        h = h % 360
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c/2
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (
            round((r + m) * 255),
            round((g + m) * 255),
            round((b + m) * 255)
        )


    def render_to_image(self, output_path: str, width: int = None, height: int = None) -> None:
        debug_print("\n=== Rendering Image ===")
        output_width = width or 400
        output_height = height or 400
        debug_print(f"Requested output: {output_width}x{output_height}")

        # Calculate scaling factors
        content_width = max(self.original_width, 1)
        content_height = max(self.original_height, 1)
        
        debug_print(f"Content size: {content_width}x{content_height}")
        debug_print(f"ViewBox: {self.view_box}")

        # Calculate aspect ratio preservation
        align, mode = self.preserve_aspect_ratio.split()
        scale_x = output_width / content_width
        scale_y = output_height / content_height

        if 'meet' in mode:
            scale = min(scale_x, scale_y)
        else:
            scale = max(scale_x, scale_y)

        scaled_w = content_width * scale
        scaled_h = content_height * scale
        tx = (output_width - scaled_w) * {'xMin':0, 'xMid':0.5, 'xMax':1}[align[1:4]]
        ty = (output_height - scaled_h) * {'YMin':0, 'YMid':0.5, 'YMax':1}[align[4:7]]

        # Create transformation matrix
        transform = [
            scale, 0, 0, scale,
            tx - (self.view_box[0] * scale if self.view_box else 0),
            ty - (self.view_box[1] * scale if self.view_box else 0)
        ]
        debug_print(f"Transformation matrix: {transform}")

        # Initialize rasterizer
        rasterizer = AntiAliasedRasterizer(output_width, output_height)
        debug_print(f"Initialized {output_width}x{output_height} rasterizer")

        # Process all paths
        for idx, path_data in enumerate(self.paths):
            path = path_data['path'].copy()
            debug_print(f"\nProcessing path {idx+1}/{len(self.paths)}")
            debug_print(f"Original elements: {len(path.elements)}")

            # Apply transformations
            if path_data['transform']:
                debug_print("Applying element transform")
                path = path.transform(*path_data['transform'])
            
            debug_print("Applying main transformation")
            transformed_path = path.transform(*transform)
            
            # Render operations
            if fill_props := path_data['fill']:
                debug_print(f"Filling with {fill_props.color}")
                rasterizer.fill_path(transformed_path, fill_props)
            
            if stroke_props := path_data['stroke']:
                stroke_scale = math.hypot(transform[0], transform[3])
                debug_print(f"Stroke scaling: {stroke_scale:.2f}x")
                scaled_stroke = StrokeProperties(
                    width=stroke_props.width * stroke_scale,
                    color=stroke_props.color,
                    line_cap=stroke_props.line_cap,
                    line_join=stroke_props.line_join,
                    miter_limit=stroke_props.miter_limit
                )
                rasterizer.stroke_path(transformed_path, scaled_stroke)

        # Save final image
        debug_print("\n=== Saving Image ===")
        save_to_png(rasterizer.get_buffer(), output_path, output_width, output_height)
        debug_print(f"Successfully saved to {output_path}")



class SVGRenderer:
    @staticmethod
    def render(svg_path: str, output_path: str, width: int = None, height: int = None) -> None:
        debug_print("\n=== Starting SVG Render ===")
        parser = SVGParser()
        parser.parse_file(svg_path)
        debug_print(f"Rendering with {width}x{height} output")
        parser.render_to_image(output_path, width, height)
        debug_print("=== Render Complete ===\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} input.svg output.png [width] [height]")
        sys.exit(1)

    try:
        width = int(sys.argv[3]) if len(sys.argv) >=4 else None
        height = int(sys.argv[4]) if len(sys.argv) >=5 else None
    except ValueError:
        print("Error: Width and height must be integers")
        sys.exit(1)

    SVGRenderer.render(sys.argv[1], sys.argv[2], width, height)
