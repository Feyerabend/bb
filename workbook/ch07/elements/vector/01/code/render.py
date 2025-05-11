#!/usr/bin/env python3

import math
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional
from copy import deepcopy
from enum import Enum


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
        
    def sample_points(self, resolution: float) -> List[Point]:
        if resolution <= 0:
            raise ValueError("Resolution must be positive")
            
        distance = self.start.distance_to(self.end)
        if distance < 1e-6:  # degenerate case
            return [deepcopy(self.start)]
            
        num_points = max(2, int(distance / resolution) + 1)
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            x = self.start.x + t * (self.end.x - self.start.x)
            y = self.start.y + t * (self.end.y - self.start.y)
            points.append(Point(x, y))
            
        return points
    
    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'LineTo':
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
            return [deepcopy(self.start)]
        
        approx_length = self._estimate_length(20)
        
        num_points = max(2, int(approx_length / resolution) + 1)
        
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            points.append(self._cubic_bezier_point(t))
            
        return points

    def _estimate_length(self, steps=10) -> float:
        length = 0.0
        last_point = self.start
        
        for i in range(1, steps + 1):
            t = i / steps
            current_point = self._cubic_bezier_point(t)
            length += last_point.distance_to(current_point)
            last_point = current_point
            
        return length

    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'CubicBezierTo':
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
    
    def move_to(self, x: float, y: float) -> 'Path':
        self.current_point = Point(x, y)
        return self
    
    def line_to(self, x: float, y: float) -> 'Path':
        if self.current_point is None:
            self.move_to(x, y)
            return self
        end_point = Point(x, y)
        self.elements.append(LineTo(self.current_point, end_point))
        self.current_point = end_point
        return self
    
    def cubic_bezier_to(self, cx1: float, cy1: float, 
                        cx2: float, cy2: float, 
                        x: float, y: float) -> 'Path':
        if self.current_point is None:
            self.move_to(x, y)
            return self
            
        ctrl1 = Point(cx1, cy1)
        ctrl2 = Point(cx2, cy2)
        end_point = Point(x, y)
        
        self.elements.append(CubicBezierTo(self.current_point, ctrl1, ctrl2, end_point))
        self.current_point = end_point
        return self
    
    def close(self) -> 'Path':
        if len(self.elements) > 0 and self.current_point is not None:
            first_point = self.elements[0].start
            if self.current_point.x != first_point.x or self.current_point.y != first_point.y:
                self.line_to(first_point.x, first_point.y)
            self.closed = True
        return self
    
    def sample_points(self, resolution: float) -> List[Point]:
        all_points = []
        for element in self.elements:
            all_points.extend(element.sample_points(resolution))
        return all_points
    
    def get_edges(self) -> List[Tuple[Point, Point]]:
        edges = []
        for element in self.elements:
            points = element.sample_points(0.25)
            if len(points) < 2:
                continue
                
            for i in range(len(points) - 1):
                edges.append((points[i], points[i + 1]))
                
        return edges

    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        points = self.sample_points(0.1)
        if not points:
            return (0.0, 0.0, 0.0, 0.0)
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return (min(xs), min(ys), max(xs), max(ys))

    def transform(self, sx: float, k: float, l: float, sy: float, tx: float, ty: float) -> 'Path':
        new_path = Path()
        new_path.closed = self.closed
        new_path.elements = [element.transform(sx, k, l, sy, tx, ty) for element in self.elements]
        new_path.current_point = self.current_point.transform(sx, k, l, sy, tx, ty) if self.current_point else None
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

class StrokeProperties:    
    def __init__(self, width: float = 1.0, color: Tuple[int, int, int, int] = (0, 0, 0, 255),
                 line_cap: LineCap = LineCap.BUTT, line_join: LineJoin = LineJoin.MITER,
                 miter_limit: float = 4.0):
        self.width = width
        self.color = color
        self.line_cap = line_cap
        self.line_join = line_join
        self.miter_limit = miter_limit

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
    
    def rasterize(self, path: Path, canvas_width: int, canvas_height: int,
                  stroke: Optional[StrokeProperties] = None,
                  fill: Optional[FillProperties] = None,
                  existing_canvas: Optional[np.ndarray] = None) -> np.ndarray:
        if existing_canvas is None:
            self.canvas = np.zeros((canvas_height, canvas_width, 4), dtype=np.uint8)
        else:
            self.canvas = existing_canvas.copy()
        
        if fill is not None:
            self.fill_path(path, fill)
        
        if stroke is not None:
            self.stroke_path(path, stroke)
        
        return self.canvas

    def fill_path(self, path: Path, fill: FillProperties) -> None:
        if not path.elements:
            return

        # Get canvas dimensions and path bounding box
        height, width = self.canvas.shape[:2]
        min_x, min_y, max_x, max_y = path.get_bounding_box()
        
        # Early exit if path is completely outside the canvas
        if min_x >= width or min_y >= height or max_x < 0 or max_y < 0:
            return
        
        # Clamp to canvas bounds and convert to integers
        min_y = max(0, int(min_y))
        max_y = min(height - 1, int(max_y) + 1)  # +1 to ensure we include max_y
        min_x = max(0, int(min_x))
        max_x = min(width - 1, int(max_x) + 1)   # +1 to ensure we include max_x
        
        # Fetch all edges once for efficiency
        all_edges = path.get_edges()
        if not all_edges:
            return
        
        # Alpha as float for blending operations
        alpha = fill.color[3] / 255.0
        
        # Process each scanline
        for y in range(min_y, max_y + 1):
            # Generate scan line segment runs
            runs = self._generate_runs(all_edges, y, width, fill.rule)
            
            # Process each run
            for start_x, end_x in runs:
                # Clamp run to canvas bounds
                start_x = max(min_x, start_x)
                end_x = min(max_x, end_x)
                
                if start_x <= end_x:
                    # Use NumPy's vectorized operations for the entire span
                    span = slice(start_x, end_x + 1)
                    
                    if alpha == 1.0:  # Fully opaque - simple replacement
                        self.canvas[y, span] = fill.color
                    else:  # Semi-transparent - blend with existing pixels
                        # Create a span-sized array of the fill color
                        span_length = end_x - start_x + 1
                        fill_array = np.full((span_length, 4), fill.color, dtype=np.uint8)
                        
                        # Get the existing pixels
                        existing = self.canvas[y, span].copy()
                        
                        # Blend using vectorized operations
                        inv_alpha = 1.0 - alpha
                        blended = np.clip(
                            existing * inv_alpha + fill_array * alpha,
                            0, 255
                        ).astype(np.uint8)
                        
                        # Update the canvas
                        self.canvas[y, span] = blended
    

    def stroke_path(self, path: Path, stroke: StrokeProperties) -> None:
        """
        Improved implementation of stroke_path that correctly handles line joins and caps.
        """
        resolution = min(0.3, stroke.width / 4)  # Adaptive resolution based on stroke width
        points = path.sample_points(resolution)
        if len(points) < 2:
            return
        
        height, width = self.canvas.shape[:2]
        half_width = stroke.width / 2
        
        # Helper functions for drawing caps and joins
        def draw_cap(point: Point, direction: Point, cap_style: LineCap):
            if cap_style == LineCap.BUTT:
                return
            
            # Normalize direction
            norm = math.sqrt(direction.x**2 + direction.y**2)
            if norm < 1e-6:
                return
            direction_normalized = Point(direction.x / norm, direction.y / norm)
            
            if cap_style == LineCap.ROUND:
                # Draw a half-circle cap
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
                        # Create a small triangle fan from center
                        self._fill_polygon([center, prev_point, cap_point], stroke.color)
                    prev_point = cap_point
            
            elif cap_style == LineCap.SQUARE:
                # Draw a square cap (extend by half_width in direction)
                extended = Point(
                    point.x + direction_normalized.x * half_width,
                    point.y + direction_normalized.y * half_width
                )
                
                # Get perpendicular vector
                perp = Point(-direction_normalized.y, direction_normalized.x)
                
                # Create square cap corners
                corners = [
                    Point(extended.x + perp.x * half_width, extended.y + perp.y * half_width),
                    Point(extended.x - perp.x * half_width, extended.y - perp.y * half_width),
                    Point(point.x - perp.x * half_width, point.y - perp.y * half_width),
                    Point(point.x + perp.x * half_width, point.y + perp.y * half_width)
                ]
                
                self._fill_polygon(corners, stroke.color)
        
        def draw_join(p1: Point, p2: Point, p3: Point, join_style: LineJoin):
            # Calculate normalized direction vectors
            v1 = Point(p2.x - p1.x, p2.y - p1.y)
            v2 = Point(p3.x - p2.x, p3.y - p2.y)
            
            len1 = math.sqrt(v1.x**2 + v1.y**2)
            len2 = math.sqrt(v2.x**2 + v2.y**2)
            
            if len1 < 1e-6 or len2 < 1e-6:
                return
            
            v1 = Point(v1.x / len1, v1.y / len1)
            v2 = Point(v2.x / len2, v2.y / len2)
            
            # Get perpendicular vectors
            perp1 = Point(-v1.y, v1.x)
            perp2 = Point(-v2.y, v2.x)
            
            # Calculate outer points of the segments
            outer1 = Point(p2.x + perp1.x * half_width, p2.y + perp1.y * half_width)
            inner1 = Point(p2.x - perp1.x * half_width, p2.y - perp1.y * half_width)
            outer2 = Point(p2.x + perp2.x * half_width, p2.y + perp2.y * half_width)
            inner2 = Point(p2.x - perp2.x * half_width, p2.y - perp2.y * half_width)
            
            # Determine if this is an inside or outside corner
            dot_product = v1.x * v2.x + v1.y * v2.y
            cross_product = v1.x * v2.y - v1.y * v2.x
            is_outside_corner = cross_product < 0
            
            if join_style == LineJoin.ROUND and is_outside_corner:
                # Draw a rounded join using a pie wedge
                steps = max(8, int(half_width))
                start_angle = math.atan2(perp1.y, perp1.x)
                end_angle = math.atan2(perp2.y, perp2.x)
                
                # Ensure we go the short way around for the rounded join
                if end_angle < start_angle:
                    end_angle += 2 * math.pi
                if end_angle - start_angle > math.pi:
                    start_angle += 2 * math.pi
                
                # Create pie wedge points
                pie_points = [p2]  # Center
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
                # For bevel join, simply connect the outer points
                if is_outside_corner:
                    self._fill_polygon([p2, outer1, outer2], stroke.color)
                else:
                    self._fill_polygon([p2, inner1, inner2], stroke.color)
                    
            elif join_style == LineJoin.MITER:
                if not is_outside_corner:
                    # Inside corners can be handled like bevel
                    self._fill_polygon([p2, inner1, inner2], stroke.color)
                    return
                
                # Calculate miter point
                # First, get the angle between the segments
                angle = math.acos(max(-1.0, min(1.0, dot_product)))
                
                # Calculate miter length
                miter_length = half_width / math.sin(angle / 2) if angle != 0 else half_width
                
                # Check miter limit
                if miter_length > stroke.miter_limit * half_width:
                    # Fallback to bevel join if miter is too long
                    self._fill_polygon([p2, outer1, outer2], stroke.color)
                    return
                
                # Calculate miter direction (bisector of the exterior angle)
                bisector_x = (perp1.x + perp2.x) / 2
                bisector_y = (perp1.y + perp2.y) / 2
                bisector_len = math.sqrt(bisector_x**2 + bisector_y**2)
                
                if bisector_len < 1e-6:
                    return
                
                # Normalize bisector
                bisector_x /= bisector_len
                bisector_y /= bisector_len
                
                # Calculate miter point
                miter_point = Point(
                    p2.x + bisector_x * miter_length,
                    p2.y + bisector_y * miter_length
                )
                
                # Create miter join
                self._fill_polygon([p2, outer1, miter_point, outer2], stroke.color)
        
        # Draw line segments
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            
            # Skip degenerate segments
            if p1.distance_to(p2) < 1e-6:
                continue
            
            direction = Point(p2.x - p1.x, p2.y - p1.y)
            length = math.sqrt(direction.x**2 + direction.y**2)
            direction = Point(direction.x / length, direction.y / length)
            
            # Get perpendicular vector
            perp = Point(-direction.y, direction.x)
            
            # Calculate the four corners of the segment rectangle
            corners = [
                Point(p1.x + perp.x * half_width, p1.y + perp.y * half_width),
                Point(p1.x - perp.x * half_width, p1.y - perp.y * half_width),
                Point(p2.x - perp.x * half_width, p2.y - perp.y * half_width),
                Point(p2.x + perp.x * half_width, p2.y + perp.y * half_width)
            ]
            
            # Fill the segment rectangle
            self._fill_polygon(corners, stroke.color)
            
            # Draw join with next segment if there is one
            if i < len(points) - 2:
                draw_join(p1, p2, points[i + 2], stroke.line_join)
        
        # Draw caps for open paths
        if not path.closed and len(points) >= 2:
            # Start cap
            start_direction = Point(points[1].x - points[0].x, points[1].y - points[0].y)
            start_length = math.sqrt(start_direction.x**2 + start_direction.y**2)
            if start_length > 1e-6:
                start_direction = Point(
                    -start_direction.x / start_length, 
                    -start_direction.y / start_length
                )
                draw_cap(points[0], start_direction, stroke.line_cap)
            
            # End cap
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

    def _sample_line(self, p1: Point, p2: Point, resolution: float) -> List[Point]:
        distance = p1.distance_to(p2)
        num_points = max(2, int(distance / resolution))
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            x = p1.x + t * (p2.x - p1.x)
            y = p1.y + t * (p2.y - p1.y)
            points.append(Point(x, y))
        return points

    def _perpendicular_vector(self, p1: Point, p2: Point, length: float) -> Point:
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
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

    def _fill_polygon(self, points: List[Point], color: Tuple[int, int, int, int]):
        min_x = max(0, int(min(p.x for p in points)))
        max_x = min(self.canvas.shape[1] - 1, int(max(p.x for p in points)))
        min_y = max(0, int(min(p.y for p in points)))
        max_y = min(self.canvas.shape[0] - 1, int(max(p.y for p in points)))
        
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
            for i in range(0, len(intersections), 2):
                start_x = max(min_x, int(intersections[i]))
                end_x = min(max_x, int(intersections[i + 1]) if i + 1 < len(intersections) else max_x)
                for x in range(start_x, end_x + 1):
                    self._plot_pixel(x, y, color, color[3])

    def _angle_between_vectors(self, v1: Point, v2: Point) -> float:
        dot = v1.x * v2.x + v1.y * v2.y
        det = v1.x * v2.y - v1.y * v2.x
        angle = math.atan2(det, dot)
        return abs(angle)

    def get_buffer(self) -> np.ndarray:
        return self.canvas
    
    def _generate_runs(self, edges: List[Tuple[Point, Point]], y: int, width: int, fill_rule: FillRule) -> List[Tuple[int, int]]:
        intersections = []
        
        # Find all intersections with this scanline
        for p1, p2 in edges:
            # Skip horizontal edges (they don't create intersections with horizontal scanlines)
            if p1.y == p2.y:
                continue
                
            # Check if the edge crosses this scanline
            if (p1.y <= y < p2.y) or (p2.y <= y < p1.y):
                # Calculate the x-coordinate of the intersection
                t = (y - p1.y) / (p2.y - p1.y)
                x_intersect = p1.x + t * (p2.x - p1.x)
                
                # Determine edge direction for winding number calculation
                direction = 1 if p2.y > p1.y else -1
                intersections.append((int(x_intersect), direction))
        
        # Sort intersections by x-coordinate
        intersections.sort(key=lambda i: i[0])
        
        # Initialize empty list of runs
        runs = []
        if not intersections:
            return runs
        
        # Apply the fill rule to determine spans to fill
        winding_number = 0
        start_x = None
        
        for x, direction in intersections:
            # Update winding number
            prev_winding = winding_number
            winding_number += direction
            
            # Check if we're transitioning from outside to inside
            prev_inside = fill_rule.is_inside(prev_winding)
            inside = fill_rule.is_inside(winding_number)
            
            if not prev_inside and inside:
                # Start a new span
                start_x = x
            elif prev_inside and not inside and start_x is not None:
                # End the current span
                runs.append((max(0, start_x), min(width - 1, x)))
                start_x = None
        
        # Handle case where path extends to edge of canvas
        if start_x is not None and fill_rule.is_inside(winding_number):
            runs.append((max(0, start_x), width - 1))
            
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

    def _blend_color(self, existing: np.ndarray, new_color: Tuple[int, int, int, int]) -> np.ndarray:
        alpha = new_color[3] / 255.0
        inv_alpha = 1 - alpha
        return np.clip(
            existing * inv_alpha + np.array(new_color) * alpha,
            0, 255
        ).astype(np.uint8)


class AntiAliasedRasterizer(SimpleRasterizer):
    def __init__(self, width: int, height: int):
        super().__init__(width * 2, height * 2)  # 2x
    
    def rasterize(self, path: Path, canvas_width: int, canvas_height: int,
                  stroke: Optional[StrokeProperties] = None,
                  fill: Optional[FillProperties] = None,
                  existing_canvas: Optional[np.ndarray] = None) -> np.ndarray:
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
        
        ss_stroke = None
        if stroke is not None:
            ss_stroke = StrokeProperties(
                width=stroke.width * ss_factor,
                color=stroke.color,
                line_cap=stroke.line_cap,
                line_join=stroke.line_join,
                miter_limit=stroke.miter_limit
            )
        
        ss_canvas = super().rasterize(path, ss_width, ss_height, ss_stroke, fill, ss_existing_canvas)
        
        canvas = np.zeros((canvas_height, canvas_width, 4), dtype=np.uint8) if existing_canvas is None else existing_canvas.copy()
        
        for y in range(canvas_height):
            for x in range(canvas_width):
                ss_region = ss_canvas[y*ss_factor:(y+1)*ss_factor, 
                                     x*ss_factor:(x+1)*ss_factor]
                canvas[y, x] = np.mean(ss_region, axis=(0, 1)).astype(np.uint8)
        
        self.canvas = canvas
        return self.canvas


# skip? or move defaults
# of rect, circle, etc. to the factory?
class PathFactory:
    @staticmethod
    def create_star(cx: float, cy: float, outer_radius: float, 
                   inner_radius: float, points: int) -> Path:
        path = Path()
        
        for i in range(points * 2):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = math.pi * i / points
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            if i == 0:
                path.move_to(x, y)
            else:
                path.line_to(x, y)
                
        path.close()
        return path
    
    @staticmethod
    def create_spiral(cx: float, cy: float, start_radius: float, 
                     end_radius: float, turns: float, segments: int) -> Path:
        path = Path()
        
        for i in range(segments + 1):
            t = i / segments
            radius = start_radius + (end_radius - start_radius) * t
            angle = turns * 2 * math.pi * t
            
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            
            if i == 0:
                path.move_to(x, y)
            else:
                path.line_to(x, y)
                
        return path


def save_to_png(canvas: np.ndarray, filename: str, width: int = None, height: int = None) -> None:
    from PIL import Image
    img = Image.fromarray(canvas)
    if width and height:
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    if not filename.lower().endswith('.png'):
        filename = filename + '.png'
    img.save(filename, format="PNG")



# ---- Example usage ----

def main():
    path = Path()
    path.move_to(50, 50)
    path.line_to(150, 50)
    path.line_to(150, 150)
    path.cubic_bezier_to(150, 200, 100, 200, 50, 150)
    path.close()
    
    star_path = PathFactory.create_star(100, 250, 50, 25, 5)
    spiral_path = PathFactory.create_spiral(250, 100, 10, 50, 3, 100)
    
    rasterizer = SimpleRasterizer(400, 400)
    enhanced_rasterizer = AntiAliasedRasterizer(400, 400)
    
    black_stroke = StrokeProperties(width=6.0, color=(0, 0, 0, 255),
                                   line_cap=LineCap.ROUND, line_join=LineJoin.ROUND)
    red_stroke = StrokeProperties(width=4.0, color=(255, 0, 0, 255),
                                 line_cap=LineCap.SQUARE, line_join=LineJoin.BEVEL)
    blue_stroke = StrokeProperties(width=4.0, color=(0, 0, 255, 255),
                                  line_cap=LineCap.BUTT, line_join=LineJoin.MITER, miter_limit=4.0)
    
    light_blue_fill = FillProperties(color=(100, 200, 255, 255), rule=EvenOddFillRule())
    yellow_fill = FillProperties(color=(255, 255, 100, 255), rule=NonZeroWindingFillRule())
    
    canvas_width, canvas_height = 400, 400
    
    canvas = rasterizer.rasterize(path, canvas_width, canvas_height, black_stroke, light_blue_fill)
    canvas = rasterizer.rasterize(star_path, canvas_width, canvas_height, red_stroke, yellow_fill, canvas)
    canvas = enhanced_rasterizer.rasterize(spiral_path, canvas_width, canvas_height, blue_stroke, existing_canvas=canvas)
    
    save_to_png(canvas, "vector_paths.png", canvas_width, canvas_height)
    print("Image saved to vector_paths.png")
    
    even_odd_path = Path()
    even_odd_path.move_to(250, 200)
    even_odd_path.line_to(350, 200)
    even_odd_path.line_to(350, 300)
    even_odd_path.line_to(250, 300)
    even_odd_path.close()
    
    even_odd_path.move_to(300, 250)
    even_odd_path.line_to(380, 250)
    even_odd_path.line_to(380, 350)
    even_odd_path.line_to(300, 350)
    even_odd_path.close()
    
    even_odd_canvas = rasterizer.rasterize(
        even_odd_path, canvas_width, canvas_height,
        black_stroke, FillProperties(color=(0, 200, 100, 255), rule=EvenOddFillRule())
    )
    save_to_png(even_odd_canvas, "even_odd_fill.png", canvas_width, canvas_height)
    print("Image saved to even_odd_fill.png")
    
    winding_canvas = rasterizer.rasterize(
        even_odd_path, canvas_width, canvas_height,
        black_stroke, FillProperties(color=(0, 200, 100, 255), rule=NonZeroWindingFillRule())
    )
    save_to_png(winding_canvas, "winding_fill.png", canvas_width, canvas_height)
    print("Image saved to winding_fill.png")


if __name__ == "__main__":
    main()