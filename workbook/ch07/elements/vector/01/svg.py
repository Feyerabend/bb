import xml.etree.ElementTree as ET
import re
from pathlib import Path as FilePath
import math
from typing import Tuple, List, Dict, Any, Optional, Union

from render import Path, PathFactory, SimpleRasterizer, AntiAliasedRasterizer
from render import StrokeProperties, FillProperties
from render import EvenOddFillRule, NonZeroWindingFillRule
from render import save_to_png, LineCap, LineJoin

class SVGParser:
    
    SVG_NS = "{http://www.w3.org/2000/svg}"
    
    def __init__(self):
        self.paths = []
        self.width = 0
        self.height = 0
        self.view_box = None
        self.preserve_aspect_ratio = 'xMidYMid meet'
        
    def parse_file(self, svg_path: str) -> None:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        self.width = self._parse_dimension(root.get('width', '0'))
        self.height = self._parse_dimension(root.get('height', '0'))
        
        view_box_str = root.get('viewBox')
        if view_box_str:
            self.view_box = [float(x) for x in view_box_str.split()]
        
        self.preserve_aspect_ratio = root.get('preserveAspectRatio', 'xMidYMid meet')
        
        self._process_element(root, parent_style={}, parent_transform=None)
    
    def _parse_dimension(self, value: str) -> float:
        if not value:
            return 0
        match = re.match(r'([0-9.]+)([a-z%]*)', value.lower())
        if not match:
            try:
                return float(value)
            except ValueError:
                return 0
        num, unit = match.groups()
        # TODO: Add support for pt, cm, mm, in, %, em, ex
        return float(num)
    
    def _parse_transform(self, transform_str: str) -> Optional[List[float]]:
        if not transform_str:
            return None
        # Default identity matrix
        matrix = [1, 0, 0, 1, 0, 0]
        for transform in re.finditer(r'(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]+)\)', transform_str):
            name, args = transform.groups()
            args = [float(x) for x in re.split(r'[\s,]+', args.strip())]
            if name == 'matrix' and len(args) == 6:
                matrix = args
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
                    matrix = self._multiply_matrices(matrix, [math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), 0, 0])
                    matrix = self._multiply_matrices(matrix, [1, 0, 0, 1, -cx, -cy])
                else:
                    matrix = self._multiply_matrices(matrix, [math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), 0, 0])
            elif name == 'skewX' and len(args) == 1:
                matrix = self._multiply_matrices(matrix, [1, 0, math.tan(math.radians(args[0])), 1, 0, 0])
            elif name == 'skewY' and len(args) == 1:
                matrix = self._multiply_matrices(matrix, [1, math.tan(math.radians(args[0])), 0, 1, 0, 0])
        return matrix
    
    def _multiply_matrices(self, m1: List[float], m2: List[float]) -> List[float]:
        a1, b1, c1, d1, e1, f1 = m1
        a2, b2, c2, d2, e2, f2 = m2
        return [
            a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1
        ]
    
    def _process_element(self, element: ET.Element, parent_style: Dict[str, str], parent_transform: Optional[List[float]]) -> None:
        """Process an SVG element and its children, passing down styles and transformations."""
        tag_name = element.tag
        if '}' in tag_name:
            tag_name = tag_name.split('}', 1)[1]
        
        current_style = parent_style.copy()
        style_str = element.get('style', '')
        if style_str:
            for item in style_str.split(';'):
                if ':' in item:
                    key, value = item.split(':', 1)
                    current_style[key.strip()] = value.strip()
        for key in ['stroke', 'stroke-width', 'stroke-opacity', 'stroke-linecap', 'stroke-linejoin', 'fill', 'fill-opacity', 'fill-rule', 'miter-limit']:
            if key in element.attrib:
                current_style[key] = element.get(key)
        
        # Parse transform attribute
        transform_str = element.get('transform', '')
        current_transform = self._parse_transform(transform_str) if transform_str else parent_transform
        if current_transform and parent_transform:
            current_transform = self._multiply_matrices(parent_transform, current_transform)
        
        if tag_name == 'svg':
            for child in element:
                self._process_element(child, current_style, current_transform)
        elif tag_name == 'path':
            self._process_path(element, current_style, current_transform)
        elif tag_name == 'rect':
            self._process_rect(element, current_style, current_transform)
        elif tag_name == 'circle':
            self._process_circle(element, current_style, current_transform)
        elif tag_name == 'ellipse':
            self._process_ellipse(element, current_style, current_transform)
        elif tag_name == 'line':
            self._process_line(element, current_style, current_transform)
        elif tag_name == 'polyline':
            self._process_polyline(element, current_style, current_transform)
        elif tag_name == 'polygon':
            self._process_polygon(element, current_style, current_transform)
        elif tag_name == 'g':
            for child in element:
                self._process_element(child, current_style, current_transform)
    
    def _process_path(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        """Process an SVG path element, involving styles and transformations."""
        d = element.get('d', '')
        if not d:
            return
        path = Path()
        try:
            self._parse_path_data(path, d)
        except ValueError as e:
            print(f"Warning: Skipping invalid path data: {e}")
            return
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
    
    def _parse_path_data(self, path: Path, d: str) -> None:
        # Replace commas with spaces, normalize whitespace
        d = re.sub(r',', ' ', d.strip())
        # Tokenize: match commands (letters) or numbers (including .5, scientific notation)
        tokens = re.findall(r'[a-zA-Z]|[+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+|\.\d+)', d)
        if not tokens:
            raise ValueError("Empty or invalid path data")
        
        i = 0
        current_x, current_y = 0, 0
        last_control_x, last_control_y = None, None
        subpath_initial_x, subpath_initial_y = 0, 0
        command = None
        
        while i < len(tokens):
            # Check if token is a command
            if i < len(tokens) and tokens[i].isalpha():
                command = tokens[i]
                i += 1
            # Ensure we have tokens to process
            if i >= len(tokens):
                break
            try:
                if command in ('M', 'm') and i + 1 < len(tokens):
                    # Moveto requires two coordinates
                    try:
                        x = float(tokens[i])
                        y = float(tokens[i + 1])
                    except (ValueError, IndexError):
                        print(f"Warning: Incomplete M/m command at token {i}, skipping")
                        i += len(tokens) - i  # Skip to end to avoid further errors
                        continue
                    if command == 'M':
                        current_x, current_y = x, y
                    else:  # m
                        current_x += x
                        current_y += y
                    subpath_initial_x, subpath_initial_y = current_x, current_y
                    path.move_to(current_x, current_y)
                    i += 2
                    command = 'L' if command == 'M' else 'l'
                elif command in ('L', 'l') and i + 1 < len(tokens):
                    x = float(tokens[i])
                    y = float(tokens[i + 1])
                    if command == 'L':
                        current_x, current_y = x, y
                    else:
                        current_x += x
                        current_y += y
                    path.line_to(current_x, current_y)
                    i += 2
                elif command in ('H', 'h') and i < len(tokens):
                    x = float(tokens[i])
                    if command == 'H':
                        current_x = x
                    else:
                        current_x += x
                    path.line_to(current_x, current_y)
                    i += 1
                elif command in ('V', 'v') and i < len(tokens):
                    y = float(tokens[i])
                    if command == 'V':
                        current_y = y
                    else:
                        current_y += y
                    path.line_to(current_x, current_y)
                    i += 1
                elif command in ('C', 'c') and i + 5 < len(tokens):
                    cp1x = float(tokens[i])
                    cp1y = float(tokens[i + 1])
                    cp2x = float(tokens[i + 2])
                    cp2y = float(tokens[i + 3])
                    end_x = float(tokens[i + 4])
                    end_y = float(tokens[i + 5])
                    if command == 'c':
                        cp1x += current_x
                        cp1y += current_y
                        cp2x += current_x
                        cp2y += current_y
                        end_x += current_x
                        end_y += current_y
                    path.cubic_bezier_to(cp1x, cp1y, cp2x, cp2y, end_x, end_y)
                    last_control_x, last_control_y = cp2x, cp2y
                    current_x, current_y = end_x, end_y
                    i += 6
                elif command in ('S', 's') and i + 3 < len(tokens):
                    cp1x = current_x + (current_x - last_control_x) if last_control_x is not None else current_x
                    cp1y = current_y + (current_y - last_control_y) if last_control_y is not None else current_y
                    cp2x = float(tokens[i])
                    cp2y = float(tokens[i + 1])
                    end_x = float(tokens[i + 2])
                    end_y = float(tokens[i + 3])
                    if command == 's':
                        cp2x += current_x
                        cp2y += current_y
                        end_x += current_x
                        end_y += current_y
                    path.cubic_bezier_to(cp1x, cp1y, cp2x, cp2y, end_x, end_y)
                    last_control_x, last_control_y = cp2x, cp2y
                    current_x, current_y = end_x, end_y
                    i += 4
                elif command in ('Q', 'q') and i + 3 < len(tokens):
                    cp1x = float(tokens[i])
                    cp1y = float(tokens[i + 1])
                    end_x = float(tokens[i + 2])
                    end_y = float(tokens[i + 3])
                    if command == 'q':
                        cp1x += current_x
                        cp1y += current_y
                        end_x += current_x
                        end_y += current_y
                    cp1x_cubic = current_x + 2/3 * (cp1x - current_x)
                    cp1y_cubic = current_y + 2/3 * (cp1y - current_y)
                    cp2x_cubic = end_x + 2/3 * (cp1x - end_x)
                    cp2y_cubic = end_y + 2/3 * (cp1y - end_y)
                    path.cubic_bezier_to(cp1x_cubic, cp1y_cubic, cp2x_cubic, cp2y_cubic, end_x, end_y)
                    last_control_x, last_control_y = cp1x, cp1y
                    current_x, current_y = end_x, end_y
                    i += 4
                elif command in ('T', 't') and i + 1 < len(tokens):
                    cp1x = current_x + (current_x - last_control_x) if last_control_x is not None else current_x
                    cp1y = current_y + (current_y - last_control_y) if last_control_y is not None else current_y
                    end_x = float(tokens[i])
                    end_y = float(tokens[i + 1])
                    if command == 't':
                        end_x += current_x
                        end_y += current_y
                    cp1x_cubic = current_x + 2/3 * (cp1x - current_x)
                    cp1y_cubic = current_y + 2/3 * (cp1y - current_y)
                    cp2x_cubic = end_x + 2/3 * (cp1x - end_x)
                    cp2y_cubic = end_y + 2/3 * (cp1y - end_y)
                    path.cubic_bezier_to(cp1x_cubic, cp1y_cubic, cp2x_cubic, cp2y_cubic, end_x, end_y)
                    last_control_x, last_control_y = cp1x, cp1y
                    current_x, current_y = end_x, end_y
                    i += 2
                elif command in ('A', 'a') and i + 6 < len(tokens):
                    rx = float(tokens[i])
                    ry = float(tokens[i + 1])
                    x_axis_rotation = float(tokens[i + 2])
                    large_arc_flag = int(float(tokens[i + 3]))
                    sweep_flag = int(float(tokens[i + 4]))
                    end_x = float(tokens[i + 5])
                    end_y = float(tokens[i + 6])
                    if command == 'a':
                        end_x += current_x
                        end_y += current_y
                    bezier_points = self._arc_to_bezier(
                        current_x, current_y, rx, ry, x_axis_rotation, 
                        large_arc_flag, sweep_flag, end_x, end_y
                    )
                    for j in range(0, len(bezier_points), 6):
                        path.cubic_bezier_to(
                            bezier_points[j], bezier_points[j + 1],
                            bezier_points[j + 2], bezier_points[j + 3],
                            bezier_points[j + 4], bezier_points[j + 5]
                        )
                    current_x, current_y = end_x, end_y
                    i += 7
                elif command in ('Z', 'z'):
                    path.close()
                    current_x, current_y = subpath_initial_x, subpath_initial_y
                    i += 1
                else:
                    print(f"Warning: Invalid or incomplete command at token {i}: {tokens[i-1:i+1]}")
                    i += 1  # Skip invalid token
            except (ValueError, IndexError) as e:
                print(f"Warning: Error processing command {command} at token {i}: {str(e)}, skipping")
                i += len(tokens) - i  # Skip to end to avoid further errors
                continue
    
    def _arc_to_bezier(self, x1: float, y1: float, rx: float, ry: float, phi: float, large_arc: int, sweep: int, x2: float, y2: float) -> List[float]:
        if x1 == x2 and y1 == y2 or rx == 0 or ry == 0:
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
        return result
    
    def _process_rect(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        x = float(element.get('x', '0'))
        y = float(element.get('y', '0'))
        width = float(element.get('width', '0'))
        height = float(element.get('height', '0'))
        rx = float(element.get('rx', '0'))
        ry = float(element.get('ry', '0'))
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
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
    
    def _process_circle(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        cx = float(element.get('cx', '0'))
        cy = float(element.get('cy', '0'))
        r = float(element.get('r', '0'))
        path = Path()
        kappa = 0.5522848
        path.move_to(cx + r, cy)
        path.cubic_bezier_to(cx + r, cy - kappa * r, cx + kappa * r, cy - r, cx, cy - r)
        path.cubic_bezier_to(cx - kappa * r, cy - r, cx - r, cy - kappa * r, cx - r, cy)
        path.cubic_bezier_to(cx - r, cy + kappa * r, cx - kappa * r, cy + r, cx, cy + r)
        path.cubic_bezier_to(cx + kappa * r, cy + r, cx + r, cy + kappa * r, cx + r, cy)
        path.close()
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
    
    def _process_ellipse(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        cx = float(element.get('cx', '0'))
        cy = float(element.get('cy', '0'))
        rx = float(element.get('rx', '0'))
        ry = float(element.get('ry', '0'))
        path = Path()
        kappa = 0.5522848
        path.move_to(cx + rx, cy)
        path.cubic_bezier_to(cx + rx, cy - kappa * ry, cx + kappa * rx, cy - ry, cx, cy - ry)
        path.cubic_bezier_to(cx - kappa * rx, cy - ry, cx - rx, cy - kappa * ry, cx - rx, cy)
        path.cubic_bezier_to(cx - rx, cy + kappa * ry, cx - kappa * rx, cy + ry, cx, cy + ry)
        path.cubic_bezier_to(cx + kappa * rx, cy + ry, cx + rx, cy + kappa * ry, cx + rx, cy)
        path.close()
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
    
    def _process_line(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        x1 = float(element.get('x1', '0'))
        y1 = float(element.get('y1', '0'))
        x2 = float(element.get('x2', '0'))
        y2 = float(element.get('y2', '0'))
        path = Path()
        path.move_to(x1, y1)
        path.line_to(x2, y2)
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': None,
            'transform': transform
        })
    
    def _process_polyline(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        points_str = element.get('points', '')
        if not points_str:
            return
        points = []
        for point in re.finditer(r'([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+|\.\d+))\s*,?\s*([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+|\.\d+))', points_str):
            points.append((float(point.group(1)), float(point.group(2))))
        if not points:
            return
        path = Path()
        path.move_to(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.line_to(x, y)
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': None,
            'transform': transform
        })
    
    def _process_polygon(self, element: ET.Element, parent_style: Dict[str, str], transform: Optional[List[float]]) -> None:
        points_str = element.get('points', '')
        if not points_str:
            return
        points = []
        for point in re.finditer(r'([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+|\.\d+))\s*,?\s*([+-]?(?:\d*\.\d+(?:[eE][+-]?\d+)?|\d+|\.\d+))', points_str):
            points.append((float(point.group(1)), float(point.group(2))))
        if not points:
            return
        path = Path()
        path.move_to(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.line_to(x, y)
        path.close()
        stroke_props, fill_props = self._get_style_properties(element, parent_style)
        self.paths.append({
            'path': path,
            'stroke': stroke_props,
            'fill': fill_props,
            'transform': transform
        })
    
    def _get_style_properties(self, element: ET.Element, parent_style: Dict[str, str]) -> Tuple[Optional[StrokeProperties], Optional[FillProperties]]:
        style_dict = parent_style.copy()
        style_str = element.get('style', '')
        if style_str:
            for item in style_str.split(';'):
                if ':' in item:
                    key, value = item.split(':', 1)
                    style_dict[key.strip()] = value.strip()
        for key in ['stroke', 'stroke-width', 'stroke-opacity', 'stroke-linecap', 'stroke-linejoin', 'fill', 'fill-opacity', 'fill-rule', 'miter-limit']:
            if key in element.attrib:
                style_dict[key] = element.get(key)
        
        stroke_props = None
        if 'stroke' in style_dict and style_dict['stroke'] != 'none':
            color = self._parse_color(style_dict['stroke'])
            width = float(style_dict.get('stroke-width', '1'))
            opacity = float(style_dict.get('stroke-opacity', '1'))
            # Parse line cap
            linecap_str = style_dict.get('stroke-linecap', 'butt').lower()
            linecap = {
                'butt': LineCap.BUTT,
                'round': LineCap.ROUND,
                'square': LineCap.SQUARE
            }.get(linecap_str, LineCap.BUTT)  # Default to BUTT if invalid
            # Parse line join
            linejoin_str = style_dict.get('stroke-linejoin', 'miter').lower()
            linejoin = {
                'miter': LineJoin.MITER,
                'round': LineJoin.ROUND,
                'bevel': LineJoin.BEVEL
            }.get(linejoin_str, LineJoin.MITER)  # Default to MITER if invalid
            # Parse miter limit
            miter_limit = float(style_dict.get('miter-limit', '4.0'))
            color = (color[0], color[1], color[2], max(1, int(color[3] * opacity)))
            stroke_props = StrokeProperties(
                color=color,
                width=width,
                line_cap=linecap,
                line_join=linejoin,
                miter_limit=miter_limit
            )
        
        fill_props = None
        if 'fill' in style_dict and style_dict['fill'] != 'none':
            color = self._parse_color(style_dict['fill'])
            opacity = float(style_dict.get('fill-opacity', '1'))
            color = (color[0], color[1], color[2], max(1, int(color[3] * opacity)))
            fill_rule_str = style_dict.get('fill-rule', 'nonzero')
            fill_rule = EvenOddFillRule() if fill_rule_str == 'evenodd' else NonZeroWindingFillRule()
            fill_props = FillProperties(color=color, rule=fill_rule)
        
        return stroke_props, fill_props
    
    def _parse_color(self, color_str: str) -> Tuple[int, int, int, int]:
        color = (0, 0, 0, 255)
        if not color_str:
            return color
        color_str = color_str.strip().lower()
        if color_str == 'currentcolor':
            return color  # TODO: Implement currentColor inheritance
        if color_str.startswith('#'):
            if len(color_str) == 4:
                r = int(color_str[1], 16) * 17
                g = int(color_str[2], 16) * 17
                b = int(color_str[3], 16) * 17
                return (r, g, b, 255)
            elif len(color_str) == 7:
                r = int(color_str[1:3], 16)
                g = int(color_str[3:5], 16)
                b = int(color_str[5:7], 16)
                return (r, g, b, 255)
            elif len(color_str) == 9:
                r = int(color_str[1:3], 16)
                g = int(color_str[3:5], 16)
                b = int(color_str[5:7], 16)
                a = int(color_str[7:9], 16)
                return (r, g, b, a)
        rgb_match = re.match(r'rgb\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*\)', color_str)
        if rgb_match:
            r = int(rgb_match.group(1)) if '%' not in rgb_match.group(1) else int(float(rgb_match.group(1)[:-1]) * 255 / 100)
            g = int(rgb_match.group(2)) if '%' not in rgb_match.group(2) else int(float(rgb_match.group(2)[:-1]) * 255 / 100)
            b = int(rgb_match.group(3)) if '%' not in rgb_match.group(3) else int(float(rgb_match.group(3)[:-1]) * 255 / 100)
            return (r, g, b, 255)
        rgba_match = re.match(r'rgba\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*([0-9.]+)\s*\)', color_str)
        if rgba_match:
            r = int(rgba_match.group(1)) if '%' not in rgba_match.group(1) else int(float(rgba_match.group(1)[:-1]) * 255 / 100)
            g = int(rgba_match.group(2)) if '%' not in rgb_match.group(2) else int(float(rgba_match.group(2)[:-1]) * 255 / 100)
            b = int(rgba_match.group(3)) if '%' not in rgb_match.group(3) else int(float(rgba_match.group(3)[:-1]) * 255 / 100)
            a = int(float(rgba_match.group(4)) * 255)
            return (r, g, b, a)
        hsl_match = re.match(r'hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)', color_str)
        if hsl_match:
            h, s, l = int(hsl_match.group(1)) / 360, int(hsl_match.group(2)) / 100, int(hsl_match.group(3)) / 100
            r, g, b = self._hsl_to_rgb(h, s, l)
            return (r, g, b, 255)
        hsla_match = re.match(r'hsla\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*,\s*([0-9.]+)\s*\)', color_str)
        if hsla_match:
            h, s, l = int(hsla_match.group(1)) / 360, int(hsla_match.group(2)) / 100, int(hsla_match.group(3)) / 100
            r, g, b = self._hsl_to_rgb(h, s, l)
            a = int(float(hsla_match.group(4)) * 255)
            return (r, g, b, a)
        named_colors = {
            'black': (0, 0, 0, 255), 'white': (255, 255, 255, 255), 'red': (255, 0, 0, 255),
            'green': (0, 128, 0, 255), 'blue': (0, 0, 255, 255), 'yellow': (255, 255, 0, 255),
            'cyan': (0, 255, 255, 255), 'magenta': (255, 0, 255, 255), 'silver': (192, 192, 192, 255),
            'gray': (128, 128, 128, 255), 'maroon': (128, 0, 0, 255), 'olive': (128, 128, 0, 255),
            'purple': (128, 0, 128, 255), 'teal': (0, 128, 128, 255), 'navy': (0, 0, 128, 255)
        }
        if color_str in named_colors:
            return named_colors[color_str]
        return color
    
    def _hsl_to_rgb(self, h: float, s: float, l: float) -> Tuple[int, int, int]:
        if s == 0:
            r = g = b = int(l * 255)
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = int(hue_to_rgb(p, q, h + 1/3) * 255)
            g = int(hue_to_rgb(p, q, h) * 255)
            b = int(hue_to_rgb(p, q, h - 1/3) * 255)
        return (r, g, b)
    
    def render_to_image(self, output_path: str, width: int = None, height: int = None) -> None:
        if width is None:
            width = int(self.width)
        if height is None:
            height = int(self.height)
        width = max(width, 1)
        height = max(height, 1)
        
        print(f"Rendering to {output_path} with dimensions {width}x{height}")
        print(f"SVG dimensions: {self.width}x{self.height}, ViewBox: {self.view_box}")
        print(f"PreserveAspectRatio: {self.preserve_aspect_ratio}")
        print(f"Number of paths parsed: {len(self.paths)}")
        
        rasterizer = AntiAliasedRasterizer(width, height)
        scale_x, scale_y = 1.0, 1.0
        translate_x, translate_y = 0.0, 0.0
        
        src_width = self.width
        src_height = self.height
        if self.view_box:
            src_width = self.view_box[2]
            src_height = self.view_box[3]
        
        if src_width <= 0 or src_height <= 0:
            print("Warning: Invalid source dimensions, using output dimensions")
            src_width = width
            src_height = height
        
        src_aspect = src_width / src_height
        dst_aspect = width / height
        
        # Parse preserveAspectRatio
        align, meet_or_slice = self.preserve_aspect_ratio.split()
        align_x, align_y = 'mid', 'mid'
        if align == 'xMinYMin':
            align_x, align_y = 'min', 'min'
        elif align == 'xMidYMin':
            align_x, align_y = 'mid', 'min'
        elif align == 'xMaxYMin':
            align_x, align_y = 'max', 'min'
        elif align == 'xMinYMid':
            align_x, align_y = 'min', 'mid'
        elif align == 'xMidYMid':
            align_x, align_y = 'mid', 'mid'
        elif align == 'xMaxYMid':
            align_x, align_y = 'max', 'mid'
        elif align == 'xMinYMax':
            align_x, align_y = 'min', 'max'
        elif align == 'xMidYMax':
            align_x, align_y = 'mid', 'max'
        elif align == 'xMaxYMax':
            align_x, align_y = 'max', 'max'
        
        if meet_or_slice == 'meet':
            if src_aspect > dst_aspect:
                scale_x = scale_y = width / src_width
                translate_y = (height - src_height * scale_y) * {'min': 0, 'mid': 0.5, 'max': 1}[align_y]
            else:
                scale_x = scale_y = height / src_height
                translate_x = (width - src_width * scale_x) * {'min': 0, 'mid': 0.5, 'max': 1}[align_x]
        else:  # slice
            if src_aspect < dst_aspect:
                scale_x = scale_y = width / src_width
                translate_y = (height - src_height * scale_y) * {'min': 0, 'mid': 0.5, 'max': 1}[align_y]
            else:
                scale_x = scale_y = height / src_height
                translate_x = (width - src_width * scale_x) * {'min': 0, 'mid': 0.5, 'max': 1}[align_x]
        
        vb_offset_x = -self.view_box[0] if self.view_box else 0
        vb_offset_y = -self.view_box[1] if self.view_box else 0
        
        scale_x = min(max(scale_x, 0.001), 1000.0)
        scale_y = min(max(scale_y, 0.001), 1000.0)
        
        print(f"Transformation: scale=({scale_x}, {scale_y}), translate=({translate_x + vb_offset_x}, {translate_y + vb_offset_y})")
        
        for i, path_data in enumerate(self.paths):
            path = path_data['path']
            stroke_props = path_data['stroke']
            fill_props = path_data['fill']
            element_transform = path_data.get('transform')
            
            print(f"Path {i}:")
            print(f"  Elements: {len(path.elements)}")
            print(f"  Closed: {path.closed}")
            print(f"  Stroke: {stroke_props}")
            print(f"  Fill: {fill_props}")
            print(f"  Transform: {element_transform}")
            
            transformed_path = path.copy()
            # Apply element-level transform
            if element_transform:
                transformed_path = transformed_path.transform(*element_transform)
            # Apply viewport transform
            transformed_path = transformed_path.transform(
                scale_x, 0, 0, scale_y,
                (translate_x + vb_offset_x) * scale_x,
                (translate_y + vb_offset_y) * scale_y
            )
            
            if fill_props:
                print(f"  Filling path with color {fill_props.color}")
                rasterizer.fill_path(transformed_path, fill_props)
            if stroke_props:
                scaled_stroke = StrokeProperties(
                    width=stroke_props.width * (scale_x + scale_y) / 2,  # Average scale for stroke
                    color=stroke_props.color,
                    line_cap=stroke_props.line_cap,
                    line_join=stroke_props.line_join,
                    miter_limit=stroke_props.miter_limit
                )
                print(f"  Stroking path with color {scaled_stroke.color}, width {scaled_stroke.width}")
                rasterizer.stroke_path(transformed_path, scaled_stroke)
        
        canvas = rasterizer.get_buffer()
        print(f"Canvas shape: {canvas.shape}")
        save_to_png(canvas, output_path, width, height)
        print(f"Saved image to {output_path}")


class SVGRenderer:
    @staticmethod
    def render(svg_path: str, output_path: str, width: int = None, height: int = None) -> None:
        parser = SVGParser()
        parser.parse_file(svg_path)
        parser.render_to_image(output_path, width, height)
        print(f"Rendered {svg_path} to {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print(f"Usage: {sys.argv[0]} input.svg output.png [width] [height]")
        sys.exit(1)
        
    svg_path = sys.argv[1]
    output_path = sys.argv[2]
    
    width = None
    height = None
    
    if len(sys.argv) >= 4:
        try:
            width = int(sys.argv[3])
        except ValueError:
            print("Error: width must be an integer")
            sys.exit(1)
    if len(sys.argv) == 5:
        try:
            height = int(sys.argv[4])
        except ValueError:
            print("Error: height must be an integer")
            sys.exit(1)
        
    SVGRenderer.render(svg_path, output_path, width, height)
