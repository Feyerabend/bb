#!/usr/bin/env python3

import math
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional
from copy import deepcopy
from enum import Enum

DEBUG = False

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


class LineCap(Enum):
    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"

class LineJoin(Enum):
    MITER = "miter"
    ROUND = "round"
    BEVEL = "bevel"


@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'Point':
        new_x = sx * self.x + k * self.y + tx
        new_y = l * self.x + sy * self.y + ty
        debug_print(f"Point transform: ({self.x}, {self.y}) -> ({new_x}, {new_y}) with matrix [{sx}, {k}, {l}, {sy}, {tx}, {ty}]")
        return Point(new_x, new_y)


class PathElement(ABC):    
    @abstractmethod
    def sample_points(self, resolution: float) -> List[Point]:
        pass

    @abstractmethod
    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'PathElement':
        pass


class LineTo(PathElement):    
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
        debug_print(f"LineTo created: start=({start.x}, {start.y}), end=({end.x}, {end.y})")
        
    def sample_points(self, resolution: float) -> List[Point]:
        if resolution <= 0:
            raise ValueError("Resolution must be positive")
            
        distance = self.start.distance_to(self.end)
        debug_print(f"LineTo sample_points: distance={distance}, resolution={resolution}")
        if distance < 1e-6:  # degenerate case
            debug_print("LineTo degenerate case, returning single point")
            return [deepcopy(self.start)]
            
        num_points = max(2, int(distance / resolution) + 1)
        debug_print(f"LineTo sampling {num_points} points")
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            x = self.start.x + t * (self.end.x - self.start.x)
            y = self.start.y + t * (self.end.y - self.start.y)
            points.append(Point(x, y))
            
        debug_print(f"LineTo sampled points: {[f'({p.x}, {p.y})' for p in points]}")
        return points
    
    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'LineTo':
        debug_print("Transforming LineTo")
        return LineTo(
            self.start.transform(sx, k, l, sy, tx, ty),
            self.end.transform(sx, k, l, sy, tx, ty)
        )


class CubicBezierTo(PathElement):
    def __init__(self, start: Point, control1: Point, control2: Point, end: Point):
        self.start = start
        self.control1 = control1
        self.control2 = control2
        self.end = end
        debug_print(f"CubicBezierTo created: start=({start.x}, {start.y}), ctrl1=({control1.x}, {control1.y}), "
                    f"ctrl2=({control2.x}, {control2.y}), end=({end.x}, {end.y})")
    
    def _cubic_bezier_point(self, t: float) -> Point:
        x = ((1-t)**3 * self.start.x + 
             3*(1-t)**2 * t * self.control1.x + 
             3*(1-t) * t**2 * self.control2.x + 
             t**3 * self.end.x)
        
        y = ((1-t)**3 * self.start.y + 
             3*(1-t)**2 * t * self.control1.y + 
             3*(1-t) * t**2 * self.control2.y + 
             t**3 * self.end.y)
             
        return Point(x, y)
    
    def sample_points(self, resolution: float) -> List[Point]:
        if resolution <= 0:
            raise ValueError("Resolution must be positive")
            
        if (self.start.distance_to(self.end) < 1e-6 and
            self.start.distance_to(self.control1) < 1e-6 and
            self.start.distance_to(self.control2) < 1e-6):
            debug_print("CubicBezierTo degenerate case, returning single point")
            return [deepcopy(self.start)]
        
        approx_length = self._estimate_length(50)
        debug_print(f"CubicBezierTo estimated length: {approx_length}")
        
        num_points = max(2, int(approx_length / resolution) + 1)
        debug_print(f"CubicBezierTo sampling {num_points} points with resolution={resolution}")
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            points.append(self._cubic_bezier_point(t))
            
        debug_print(f"CubicBezierTo sampled points: {[f'({p.x}, {p.y})' for p in points]}")
        return points

    def _estimate_length(self, steps=50) -> float:
        length = 0.0
        last_point = self.start
        
        for i in range(1, steps + 1):
            t = i / steps
            current_point = self._cubic_bezier_point(t)
            length += last_point.distance_to(current_point)
            last_point = current_point
            
        return length

    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'CubicBezierTo':
        debug_print("Transforming CubicBezierTo")
        return CubicBezierTo(
            self.start.transform(sx, k, l, sy, tx, ty),
            self.control1.transform(sx, k, l, sy, tx, ty),
            self.control2.transform(sx, k, l, sy, tx, ty),
            self.end.transform(sx, k, l, sy, tx, ty)
        )


class Path:    
    def __init__(self):
        self.elements: List[PathElement] = []
        self.current_point: Optional[Point] = None
        self.closed = False
        debug_print("Path initialized")
    
    def move_to(self, x: float, y: float) -> 'Path':
        self.current_point = Point(x, y)
        debug_print(f"Path move_to: ({x}, {y})")
        return self
    
    def line_to(self, x: float, y: float) -> 'Path':
        if self.current_point is None:
            self.move_to(x, y)
            debug_print(f"Path line_to with no current point, moved to: ({x}, {y})")
            return self
        end_point = Point(x, y)
        self.elements.append(LineTo(self.current_point, end_point))
        self.current_point = end_point
        debug_print(f"Path line_to: ({x}, {y})")
        return self
    
    def cubic_bezier_to(self, cx1: float, cy1: float, 
                        cx2: float, cy2: float, 
                        x: float, y: float) -> 'Path':
        if self.current_point is None:
            self.move_to(x, y)
            debug_print(f"Path cubic_bezier_to with no current point, moved to: ({x}, {y})")
            return self
            
        ctrl1 = Point(cx1, cy1)
        ctrl2 = Point(cx2, cy2)
        end_point = Point(x, y)
        
        self.elements.append(CubicBezierTo(self.current_point, ctrl1, ctrl2, end_point))
        self.current_point = end_point
        debug_print(f"Path cubic_bezier_to: ctrl1=({cx1}, {cy1}), ctrl2=({cx2}, {cy2}), end=({x}, {y})")
        return self
    
    def close(self) -> 'Path':
        if len(self.elements) > 0 and self.current_point is not None:
            first_point = self.elements[0].start
            if self.current_point.x != first_point.x or self.current_point.y != first_point.y:
                self.line_to(first_point.x, first_point.y)
                debug_print(f"Path close: added line to first point ({first_point.x}, {first_point.y})")
            self.closed = True
            debug_print("Path closed")
        return self
    
    def sample_points(self, resolution: float) -> List[Point]:
        all_points = []
        for element in self.elements:
            points = element.sample_points(resolution)
            all_points.extend(points)
        debug_print(f"Path sample_points: resolution={resolution}, total points={len(all_points)}")
        return all_points
    
    def get_edges(self) -> List[Tuple[Point, Point]]:
        edges = []
        for element in self.elements:
            points = element.sample_points(0.05)
            if len(points) < 2:
                debug_print("Path get_edges: skipping element with < 2 points")
                continue
                
            for i in range(len(points) - 1):
                edges.append((points[i], points[i + 1]))
                
        debug_print(f"Path get_edges: generated {len(edges)} edges")
        return edges

    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        points = self.sample_points(0.02)
        if not points:
            debug_print("Path get_bounding_box: no points, returning (0,0,0,0)")
            return (0.0, 0.0, 0.0, 0.0)
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        debug_print(f"Path get_bounding_box: min_x={bbox[0]}, min_y={bbox[1]}, max_x={bbox[2]}, max_y={bbox[3]}")
        return bbox

    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'Path':
        debug_print(f"Path transform: matrix=[{sx}, {k}, {l}, {sy}, {tx}, {ty}]")
        new_path = Path()
        new_path.closed = self.closed
        new_path.elements = [element.transform(sx, k, l, sy, tx, ty) for element in self.elements]
        new_path.current_point = self.current_point.transform(sx, k, l, sy, tx, ty) if self.current_point else None
        debug_print(f"Path transform: new path has {len(new_path.elements)} elements")
        return new_path
    
    def copy(self) -> 'Path':
        return deepcopy(self)


class FillRule(ABC):    
    @abstractmethod
    def is_inside(self, crossings: int) -> bool:
        pass

class EvenOddFillRule(FillRule):    
    def is_inside(self, crossings: int) -> bool:
        return crossings % 2 == 1

class NonZeroWindingFillRule(FillRule):
    def is_inside(self, crossings: int) -> bool:
        return crossings != 0

class FillProperties:    
    def __init__(self, color: Tuple[int, int, int, int] = (0, 0, 0, 255), 
                 rule: FillRule = EvenOddFillRule()):
        self.color = color
        self.rule = rule
        debug_print(f"FillProperties: color={color}, rule={type(rule).__name__}")

class StrokeProperties:    
    def __init__(self, width: float = 1.0, color: Tuple[int, int, int, int] = (0, 0, 0, 255),
                 line_cap: LineCap = LineCap.BUTT, line_join: LineJoin = LineJoin.MITER,
                 miter_limit: float = 4.0):
        self.width = width
        self.color = color
        self.line_cap = line_cap
        self.line_join = line_join
        self.miter_limit = miter_limit
        debug_print(f"StrokeProperties: width={width}, color={color}, line_cap={line_cap}, "
                    f"line_join={line_join}, miter_limit={miter_limit}")

class Rasterizer(ABC):
    @abstractmethod
    def rasterize(self, path: Path, canvas_width: int, canvas_height: int, 
                  stroke: Optional[StrokeProperties] = None,
                  fill: Optional[FillProperties] = None,
                  existing_canvas: Optional[np.ndarray] = None) -> np.ndarray:
        pass
    
    @abstractmethod
    def fill_path(self, path: Path, fill: FillProperties) -> None:
        pass
    
    @abstractmethod
    def stroke_path(self, path: Path, stroke: StrokeProperties) -> None:
        pass
    
    @abstractmethod
    def get_buffer(self) -> np.ndarray:
        pass


class SimpleRasterizer(Rasterizer):    
    def __init__(self, width: int, height: int):
        self.canvas = np.zeros((height, width, 4), dtype=np.uint8)
        debug_print(f"SimpleRasterizer initialized: canvas={width}x{height}")
    
    def rasterize(self, path: Path, canvas_width: int, canvas_height: int,
                  stroke: Optional[StrokeProperties] = None,
                  fill: Optional[FillProperties] = None,
                  existing_canvas: Optional[np.ndarray] = None) -> np.ndarray:
        debug_print(f"Rasterizing: canvas={canvas_width}x{canvas_height}, stroke={stroke is not None}, fill={fill is not None}")
        if existing_canvas is None:
            self.canvas = np.zeros((canvas_height, canvas_width, 4), dtype=np.uint8)
            debug_print("Created new canvas")
        else:
            self.canvas = existing_canvas.copy()
            debug_print("Using existing canvas")
        
        if fill is not None:
            self.fill_path(path, fill)
        
        if stroke is not None:
            self.stroke_path(path, stroke)
        
        debug_print("Rasterization complete")
        return self.canvas

    def fill_path(self, path: Path, fill: FillProperties) -> None:
        debug_print("Starting fill_path")
        if not path.elements:
            debug_print("fill_path: no elements, skipping")
            return

        # Check if path is effectively closed
        effective_path = path.copy()
        if not effective_path.closed and effective_path.elements:
            first_point = effective_path.elements[0].start
            last_point = effective_path.current_point
            if (last_point and
                abs(last_point.x - first_point.x) < 1e-6 and
                abs(last_point.y - first_point.y) < 1e-6):
                effective_path.close()
                debug_print("fill_path: auto-closed path")

        # Get canvas dimensions and path bounding box
        height, width = self.canvas.shape[:2]
        min_x, min_y, max_x, max_y = effective_path.get_bounding_box()
        debug_print(f"fill_path: canvas={width}x{height}, bbox=({min_x}, {min_y}, {max_x}, {max_y})")
        
        # Early exit if path is completely outside the canvas
        if min_x >= width or min_y >= height or max_x < 0 or max_y < 0:
            debug_print("fill_path: path outside canvas, skipping")
            return
        
        # Clamp to canvas bounds
        min_y = max(0, int(min_y))
        max_y = min(height - 1, int(max_y) + 1)
        min_x = max(0, int(min_x))
        max_x = min(width - 1, int(max_x) + 1)
        debug_print(f"fill_path: clamped bounds: x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
        
        # Fetch all edges
        all_edges = effective_path.get_edges()
        debug_print(f"fill_path: {len(all_edges)} edges generated")
        if not all_edges:
            debug_print("fill_path: no edges, skipping")
            return
        
        # Alpha for blending
        alpha = fill.color[3] / 255.0
        debug_print(f"fill_path: fill alpha={alpha}")
        
        # Process each scanline
        for y in range(min_y, max_y + 1):
            runs = self._generate_runs(all_edges, y, width, fill.rule)
            debug_print(f"fill_path: y={y}, {len(runs)} runs generated")
            
            for start_x, end_x in runs:
                start_x = max(min_x, start_x)
                end_x = min(max_x, end_x)
                debug_print(f"fill_path: run x=[{start_x}, {end_x}]")
                
                if start_x <= end_x:
                    span = slice(start_x, end_x + 1)
                    if alpha == 1.0:
                        self.canvas[y, span] = fill.color
                        debug_print(f"fill_path: filled span y={y}, x=[{start_x}, {end_x}]")
                    else:
                        span_length = end_x - start_x + 1
                        fill_array = np.full((span_length, 4), fill.color, dtype=np.uint8)
                        existing = self.canvas[y, span].copy()
                        inv_alpha = 1.0 - alpha
                        blended = np.clip(
                            existing * inv_alpha + fill_array * alpha,
                            0, 255
                        ).astype(np.uint8)
                        self.canvas[y, span] = blended
                        debug_print(f"fill_path: blended span y={y}, x=[{start_x}, {end_x}]")
    

    def stroke_path(self, path: Path, stroke: StrokeProperties) -> None:
        debug_print(f"Starting stroke_path: width={stroke.width}")
        resolution = min(0.05, stroke.width / 4)
        points = path.sample_points(resolution)
        debug_print(f"stroke_path: sampled {len(points)} points")
        if len(points) < 2:
            debug_print("stroke_path: < 2 points, skipping")
            return
        
        height, width = self.canvas.shape[:2]
        half_width = stroke.width / 2
        
        def draw_cap(point: Point, direction: Point, cap_style: LineCap):
            if cap_style == LineCap.BUTT:
                return
            norm = math.sqrt(direction.x**2 + direction.y**2)
            if norm < 1e-6:
                debug_print("draw_cap: zero norm, skipping")
                return
            direction_normalized = Point(direction.x / norm, direction.y / norm)
            debug_print(f"draw_cap: point=({point.x}, {point.y}), direction=({direction_normalized.x}, {direction_normalized.y}), style={cap_style}")
            
            if cap_style == LineCap.ROUND:
                center = point
                steps = max(8, int(half_width * 2))
                start_angle = math.atan2(-direction_normalized.y, -direction_normalized.x)
                end_angle = start_angle + math.pi
                
                prev_point = None
                for i in range(steps + 1):
                    angle = start_angle + (end_angle - start_angle) * (i / steps)
                    cap_point = Point(
                        center.x + half_width * math.cos(angle),
                        center.y + half_width * math.sin(angle)
                    )
                    if prev_point:
                        self._fill_polygon([center, prev_point, cap_point], stroke.color)
                    prev_point = cap_point
            
            elif cap_style == LineCap.SQUARE:
                extended = Point(
                    point.x + direction_normalized.x * half_width,
                    point.y + direction_normalized.y * half_width
                )
                perp = Point(-direction_normalized.y, direction_normalized.x)
                corners = [
                    Point(extended.x + perp.x * half_width, extended.y + perp.y * half_width),
                    Point(extended.x - perp.x * half_width, extended.y - perp.y * half_width),
                    Point(point.x - perp.x * half_width, point.y - perp.y * half_width),
                    Point(point.x + perp.x * half_width, point.y + perp.y * half_width)
                ]
                self._fill_polygon(corners, stroke.color)
        
        def draw_join(p1: Point, p2: Point, p3: Point, join_style: LineJoin):
            v1 = Point(p2.x - p1.x, p2.y - p1.y)
            v2 = Point(p3.x - p2.x, p3.y - p2.y)
            len1 = math.sqrt(v1.x**2 + v1.y**2)
            len2 = math.sqrt(v2.x**2 + v2.y**2)
            
            if len1 < 1e-6 or len2 < 1e-6:
                debug_print("draw_join: zero length vector, skipping")
                return
            
            v1 = Point(v1.x / len1, v1.y / len1)
            v2 = Point(v2.x / len2, v2.y / len2)
            perp1 = Point(-v1.y, v1.x)
            perp2 = Point(-v2.y, v2.x)
            outer1 = Point(p2.x + perp1.x * half_width, p2.y + perp1.y * half_width)
            inner1 = Point(p2.x - perp1.x * half_width, p2.y - perp1.y * half_width)
            outer2 = Point(p2.x + perp2.x * half_width, p2.y + perp2.y * half_width)
            inner2 = Point(p2.x - perp2.x * half_width, p2.y - perp2.y * half_width)
            dot_product = v1.x * v2.x + v1.y * v2.y
            cross_product = v1.x * v2.y - v1.y * v2.x
            is_outside_corner = cross_product < 0
            debug_print(f"draw_join: p2=({p2.x}, {p2.y}), style={join_style}, outside_corner={is_outside_corner}")
            
            if join_style == LineJoin.ROUND and is_outside_corner:
                steps = max(8, int(half_width))
                start_angle = math.atan2(perp1.y, perp1.x)
                end_angle = math.atan2(perp2.y, perp2.x)
                if end_angle < start_angle:
                    end_angle += 2 * math.pi
                if end_angle - start_angle > math.pi:
                    start_angle += 2 * math.pi
                pie_points = [p2]
                for i in range(steps + 1):
                    t = i / steps
                    angle = start_angle * (1 - t) + end_angle * t
                    pie_point = Point(
                        p2.x + half_width * math.cos(angle),
                        p2.y + half_width * math.sin(angle)
                    )
                    pie_points.append(pie_point)
                self._fill_polygon(pie_points, stroke.color)
                
            elif join_style == LineJoin.BEVEL:
                if is_outside_corner:
                    self._fill_polygon([p2, outer1, outer2], stroke.color)
                else:
                    self._fill_polygon([p2, inner1, inner2], stroke.color)
                    
            elif join_style == LineJoin.MITER:
                if not is_outside_corner:
                    self._fill_polygon([p2, inner1, inner2], stroke.color)
                    return
                angle = math.acos(max(-1.0, min(1.0, dot_product)))
                miter_length = half_width / math.sin(angle / 2) if angle != 0 else half_width
                if miter_length > stroke.miter_limit * half_width:
                    self._fill_polygon([p2, outer1, outer2], stroke.color)
                    return
                bisector_x = (perp1.x + perp2.x) / 2
                bisector_y = (perp1.y + perp2.y) / 2
                bisector_len = math.sqrt(bisector_x**2 + bisector_y**2)
                if bisector_len < 1e-6:
                    debug_print("draw_join: zero bisector length, skipping")
                    return
                bisector_x /= bisector_len
                bisector_y /= bisector_len
                miter_point = Point(
                    p2.x + bisector_x * miter_length,
                    p2.y + bisector_y * miter_length
                )
                self._fill_polygon([p2, outer1, miter_point, outer2], stroke.color)
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            if p1.distance_to(p2) < 1e-6:
                debug_print(f"stroke_path: skipping degenerate segment ({p1.x}, {p1.y}) to ({p2.x}, {p2.y})")
                continue
            direction = Point(p2.x - p1.x, p2.y - p1.y)
            length = math.sqrt(direction.x**2 + direction.y**2)
            direction = Point(direction.x / length, direction.y / length)
            perp = Point(-direction.y, direction.x)
            corners = [
                Point(p1.x + perp.x * half_width, p1.y + perp.y * half_width),
                Point(p1.x - perp.x * half_width, p1.y - perp.y * half_width),
                Point(p2.x - perp.x * half_width, p2.y - perp.y * half_width),
                Point(p2.x + perp.x * half_width, p2.y + perp.y * half_width)
            ]
            self._fill_polygon(corners, stroke.color)
            debug_print(f"stroke_path: drew segment from ({p1.x}, {p1.y}) to ({p2.x}, {p2.y})")
            if i < len(points) - 2:
                draw_join(p1, p2, points[i + 2], stroke.line_join)
        
        if not path.closed and len(points) >= 2:
            start_direction = Point(points[1].x - points[0].x, points[1].y - points[0].y)
            start_length = math.sqrt(start_direction.x**2 + start_direction.y**2)
            if start_length > 1e-6:
                start_direction = Point(
                    -start_direction.x / start_length, 
                    -start_direction.y / start_length
                )
                draw_cap(points[0], start_direction, stroke.line_cap)
            end_direction = Point(points[-1].x - points[-2].x, points[-1].y - points[-2].y)
            end_length = math.sqrt(end_direction.x**2 + end_direction.y**2)
            if end_length > 1e-6:
                end_direction = Point(
                    end_direction.x / end_length, 
                    end_direction.y / end_length
                )
                draw_cap(points[-1], end_direction, stroke.line_cap)

    
    def _draw_line_segment(self, p1: Point, p2: Point, stroke: StrokeProperties):
        v = self._perpendicular_vector(p1, p2, stroke.width / 2)
        corners = [
            Point(p1.x + v.x, p1.y + v.y),
            Point(p1.x - v.x, p1.y - v.y),
            Point(p2.x - v.x, p2.y - v.y),
            Point(p2.x + v.x, p2.y + v.y)
        ]
        self._fill_polygon(corners, stroke.color)
        points = self._sample_line(p1, p2, 0.5)
        for point in points:
            x, y = int(point.x), int(point.y)
            if 0 <= x < self.canvas.shape[1] and 0 <= y < self.canvas.shape[0]:
                self._plot_pixel(x, y, stroke.color, stroke.color[3])
                debug_print(f"_draw_line_segment: plotted pixel at ({x}, {y})")

    def _sample_line(self, p1: Point, p2: Point, resolution: float) -> List[Point]:
        distance = p1.distance_to(p2)
        num_points = max(2, int(distance / resolution))
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            x = p1.x + t * (p2.x - p1.x)
            y = p1.y + t * (p2.y - p1.y)
            points.append(Point(x, y))
        debug_print(f"_sample_line: sampled {len(points)} points")
        return points

    def _perpendicular_vector(self, p1: Point, p2: Point, length: float) -> Point:
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            debug_print("_perpendicular_vector: zero distance, returning default")
            return Point(0, length)
        dx, dy = -dy / dist, dx / dist
        return Point(dx * length, dy * length)

    def _draw_circle(self, cx: int, cy: int, radius: float, color: Tuple[int, int, int, int]):
        r = max(1, int(radius))
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                dist = math.sqrt(dx**2 + dy**2)
                if dist <= radius:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < self.canvas.shape[1] and 0 <= y < self.canvas.shape[0]:
                        opacity = int(color[3] * (1 - max(0, dist - radius + 1)))
                        self._plot_pixel(x, y, color, opacity)
                        debug_print(f"_draw_circle: plotted pixel at ({x}, {y})")

    def _fill_polygon(self, points: List[Point], color: Tuple[int, int, int, int]):
        min_x = max(0, int(min(p.x for p in points)))
        max_x = min(self.canvas.shape[1] - 1, int(max(p.x for p in points)))
        min_y = max(0, int(min(p.y for p in points)))
        max_y = min(self.canvas.shape[0] - 1, int(max(p.y for p in points)))
        debug_print(f"_fill_polygon: bounds x=[{min_x}, {max_x}], y=[{min_y}, {max_y}]")
        
        for y in range(min_y, max_y + 1):
            intersections = []
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                if (p1.y <= y < p2.y) or (p2.y <= y < p1.y):
                    if p2.y != p1.y:
                        t = (y - p1.y) / (p2.y - p1.y)
                        x_intersect = p1.x + t * (p2.x - p1.x)
                        intersections.append(x_intersect)
            intersections.sort()
            debug_print(f"_fill_polygon: y={y}, {len(intersections)} intersections")
            for i in range(0, len(intersections), 2):
                start_x = max(min_x, int(intersections[i]))
                end_x = min(max_x, int(intersections[i + 1]) if i + 1 < len(intersections) else max_x)
                for x in range(start_x, end_x + 1):
                    self._plot_pixel(x, y, color, color[3])
                    debug_print(f"_fill_polygon: plotted pixel at ({x}, {y})")

    def _angle_between_vectors(self, v1: Point, v2: Point) -> float:
        dot = v1.x * v2.x + v1.y * v2.y
        det = v1.x * v2.y - v1.y * v2.x
        angle = math.atan2(det, dot)
        return abs(angle)

    def get_buffer(self) -> np.ndarray:
        debug_print("get_buffer: returning canvas")
        return self.canvas
    
    def _generate_runs(self, edges: List[Tuple[Point, Point]], y: int, width: int, fill_rule: FillRule) -> List[Tuple[int, int]]:
        intersections = []
        for p1, p2 in edges:
            if p1.y == p2.y:
                continue
            if (p1.y <= y < p2.y) or (p2.y <= y < p1.y):
                t = (y - p1.y) / (p2.y - p1.y)
                x_intersect = p1.x + t * (p2.x - p1.x)
                direction = 1 if p2.y > p1.y else -1
                intersections.append((int(x_intersect), direction))
        intersections.sort(key=lambda i: i[0])
        debug_print(f"_generate_runs: y={y}, {len(intersections)} intersections")
        
        runs = []
        if not intersections:
            debug_print("_generate_runs: no intersections, returning empty runs")
            return runs
        
        winding_number = 0
        start_x = None
        for x, direction in intersections:
            prev_winding = winding_number
            winding_number += direction
            prev_inside = fill_rule.is_inside(prev_winding)
            inside = fill_rule.is_inside(winding_number)
            debug_print(f"_generate_runs: x={x}, direction={direction}, winding={winding_number}, inside={inside}")
            if not prev_inside and inside:
                start_x = x
            elif prev_inside and not inside and start_x is not None:
                runs.append((max(0, start_x), min(width - 1, x)))
                debug_print(f"_generate_runs: added run [{start_x}, {x}]")
                start_x = None
        
        if start_x is not None and fill_rule.is_inside(winding_number):
            runs.append((max(0, start_x), width - 1))
            debug_print(f"_generate_runs: added run [{start_x}, {width-1}]")
            
        return runs
    
    def _plot_pixel(self, x: int, y: int, color: Tuple[int, int, int, int], opacity: int):
        if opacity > 0 and 0 <= x < self.canvas.shape[1] and 0 <= y < self.canvas.shape[0]:
            current = self.canvas[y, x].copy()
            a_src = opacity / 255.0
            a_dst = current[3] / 255.0
            a_out = a_src + a_dst * (1 - a_src)
            if a_out > 0:
                for i in range(3):
                    self.canvas[y, x, i] = int((color[i] * a_src + current[i] * a_dst * (1 - a_src)) / a_out)
                self.canvas[y, x, 3] = int(a_out * 255)
                debug_print(f"_plot_pixel: plotted at ({x}, {y}), color={color}, opacity={opacity}")

    def _blend_color(self, existing: np.ndarray, new_color: Tuple[int, int, int, int]) -> np.ndarray:
        alpha = new_color[3] / 255.0
        inv_alpha = 1 - alpha
        return np.clip(
            existing * inv_alpha + np.array(new_color) * alpha,
            0, 255
        ).astype(np.uint8)


class AntiAliasedRasterizer(SimpleRasterizer):
    def __init__(self, width: int, height: int):
        super().__init__(width * 2, height * 2)
        debug_print(f"AntiAliasedRasterizer initialized: supersampled canvas={width*2}x{height*2}")
    
    def rasterize(self, path: Path, canvas_width: int, canvas_height: int,
                  stroke: Optional[StrokeProperties] = None,
                  fill: Optional[FillProperties] = None,
                  existing_canvas: Optional[np.ndarray] = None) -> np.ndarray:
        debug_print(f"AntiAliasedRasterizer rasterize: output={canvas_width}x{canvas_height}")
        ss_factor = 2
        ss_width = canvas_width * ss_factor
        ss_height = canvas_height * ss_factor
        
        ss_existing_canvas = None
        if existing_canvas is not None:
            ss_existing_canvas = np.zeros((ss_height, ss_width, 4), dtype=np.uint8)
            for y in range(canvas_height):
                for x in range(canvas_width):
                    y_ss = y * ss_factor
                    x_ss = x * ss_factor
                    ss_existing_canvas[y_ss:y_ss+ss_factor, x_ss:x_ss+ss_factor] = existing_canvas[y, x]
            debug_print("AntiAliasedRasterizer: upscaled existing canvas")
        
        ss_stroke = None
        if stroke is not None:
            min_width = 0.5 / ss_factor
            ss_stroke = StrokeProperties(
                width=max(stroke.width * ss_factor, min_width * ss_factor),
                color=stroke.color,
                line_cap=stroke.line_cap,
                line_join=stroke.line_join,
                miter_limit=stroke.miter_limit
            )
            debug_print(f"AntiAliasedRasterizer: scaled stroke width from {stroke.width} to {ss_stroke.width}")
        
        ss_canvas = super().rasterize(path, ss_width, ss_height, ss_stroke, fill, ss_existing_canvas)
        debug_print("AntiAliasedRasterizer: completed supersampled rendering")
        
        canvas = np.zeros((canvas_height, canvas_width, 4), dtype=np.uint8) if existing_canvas is None else existing_canvas.copy()
        
        for y in range(canvas_height):
            for x in range(canvas_width):
                ss_region = ss_canvas[y*ss_factor:(y+1)*ss_factor, 
                                     x*ss_factor:(x+1)*ss_factor]
                canvas[y, x] = np.mean(ss_region, axis=(0, 1)).astype(np.uint8)
                if np.any(canvas[y, x] != 0):
                    debug_print(f"AntiAliasedRasterizer: downscaled pixel at ({x}, {y}) = {canvas[y, x]}")
        
        self.canvas = canvas
        debug_print("AntiAliasedRasterizer: downscaling complete")
        return self.canvas


def save_to_png(canvas: np.ndarray, filename: str, width: int = None, height: int = None) -> None:
    from PIL import Image
    img = Image.fromarray(canvas)
    if width and height:
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        debug_print(f"save_to_png: resized to {width}x{height}")
    if not filename.lower().endswith('.png'):
        filename = filename + '.png'
    img.save(filename, format="PNG")
    debug_print(f"save_to_png: saved to {filename}")

