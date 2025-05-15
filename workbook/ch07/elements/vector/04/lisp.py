#!/usr/bin/env python3

import re
from typing import List, Dict, Any, Callable, Optional, Union, Tuple
import math
import numpy as np
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    from render import (
        Path, Point, StrokeProperties, FillProperties, AntiAliasedRasterizer, DashedStroke,
        EvenOddFillRule, NonZeroWindingFillRule, LineCap, LineJoin, save_to_png
    )
    from svg import SVGParser
except ImportError:
    print("Warning: render.py or svg.py not found. Graphics commands will be disabled.")
    Path = Point = StrokeProperties = FillProperties = AntiAliasedRasterizer = None
    EvenOddFillRule = NonZeroWindingFillRule = LineCap = LineJoin = save_to_png = None
    SVGParser = None

class LispError(Exception):
    pass

class SyntaxError(LispError):
    pass

class RuntimeError(LispError):
    pass

@dataclass
class GraphicsState:
    rasterizer: Optional[AntiAliasedRasterizer]
    current_path: Optional[Path]
    stroke_props: Optional[Union[StrokeProperties, Any]]
    fill_props: Optional[FillProperties]
    canvas_width: int
    canvas_height: int
    transform: List[float]  # [sx, k, l, sy, tx, ty]

class Transform:
    @staticmethod
    def identity() -> List[float]:
        return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    @staticmethod
    def multiply(a: List[float], b: List[float]) -> List[float]:
        return [
            a[0] * b[0] + a[2] * b[1],
            a[1] * b[0] + a[3] * b[1],
            a[0] * b[2] + a[2] * b[3],
            a[1] * b[2] + a[3] * b[3],
            a[0] * b[4] + a[2] * b[5] + a[4],
            a[1] * b[4] + a[3] * b[5] + a[5]
        ]

    @staticmethod
    def translate(dx: float, dy: float) -> List[float]:
        return [1.0, 0.0, 0.0, 1.0, dx, dy]

    @staticmethod
    def rotate(angle: float, cx: Optional[float] = None, cy: Optional[float] = None) -> List[float]:
        angle = math.radians(angle)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        if cx is not None and cy is not None:
            m1 = Transform.translate(cx, cy)
            m2 = [cos_a, sin_a, -sin_a, cos_a, 0, 0]
            m3 = Transform.translate(-cx, -cy)
            return Transform.multiply(Transform.multiply(m1, m2), m3)
        return [cos_a, sin_a, -sin_a, cos_a, 0, 0]

    @staticmethod
    def scale(sx: float, sy: float) -> List[float]:
        return [sx, 0.0, 0.0, sy, 0.0, 0.0]

class GraphicsCommand(ABC):
    @abstractmethod
    def execute(self, context: 'GraphicsContext') -> None:
        pass

class DrawLineCommand(GraphicsCommand):
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def execute(self, context: 'GraphicsContext') -> None:
        if Path:
            path = Path().move_to(self.x1, self.y1).line_to(self.x2, self.y2)
            context.set_current_path(path)
            context.render()

class DrawCircleCommand(GraphicsCommand):
    def __init__(self, cx: float, cy: float, radius: float):
        self.cx, self.cy, self.radius = cx, cy, radius

    def execute(self, context: 'GraphicsContext') -> None:
        if not Path:
            return
        kappa = 0.5522848
        r = self.radius
        path = Path()
        path.move_to(self.cx + r, self.cy)
        path.cubic_bezier_to(self.cx + r, self.cy - kappa * r, self.cx + kappa * r, self.cy - r, self.cx, self.cy - r)
        path.cubic_bezier_to(self.cx - kappa * r, self.cy - r, self.cx - r, self.cy - kappa * r, self.cx - r, self.cy)
        path.cubic_bezier_to(self.cx - r, self.cy + kappa * r, self.cx - kappa * r, self.cy + r, self.cx, self.cy + r)
        path.cubic_bezier_to(self.cx + kappa * r, self.cy + r, self.cx + r, self.cy + kappa * r, self.cx + r, self.cy)
        path.close()
        context.set_current_path(path)
        context.render()

class DrawRectangleCommand(GraphicsCommand):
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x, self.y, self.width, self.height = x, y, width, height

    def execute(self, context: 'GraphicsContext') -> None:
        if Path:
            path = Path().move_to(self.x, self.y).line_to(self.x + self.width, self.y).line_to(self.x + self.width, self.y + self.height).line_to(self.x, self.y + self.height).close()
            context.set_current_path(path)
            context.render()

class DrawEllipseCommand(GraphicsCommand):
    def __init__(self, cx: float, cy: float, rx: float, ry: float):
        self.cx, self.cy, self.rx, self.ry = cx, cy, rx, ry

    def execute(self, context: 'GraphicsContext') -> None:
        if not Path:
            return
        kappa = 0.5522848
        path = Path()
        path.move_to(self.cx + self.rx, self.cy)
        path.cubic_bezier_to(self.cx + self.rx, self.cy - kappa * self.ry, self.cx + kappa * self.rx, self.cy - self.ry, self.cx, self.cy - self.ry)
        path.cubic_bezier_to(self.cx - kappa * self.rx, self.cy - self.ry, self.cx - self.rx, self.cy - kappa * self.ry, self.cx - self.rx, self.cy)
        path.cubic_bezier_to(self.cx - self.rx, self.cy + kappa * self.ry, self.cx - kappa * self.rx, self.cy + self.ry, self.cx, self.cy + self.ry)
        path.cubic_bezier_to(self.cx + kappa * self.rx, self.cy + self.ry, self.cx + self.rx, self.cy + kappa * self.ry, self.cx + self.rx, self.cy)
        path.close()
        context.set_current_path(path)
        context.render()

class DrawPathCommand(GraphicsCommand):
    def __init__(self, path_data: str):
        self.path_data = path_data

    def execute(self, context: 'GraphicsContext') -> None:
        if not SVGParser or not Path:
            raise RuntimeError("SVG parsing not available")
        parser = SVGParser()
        path = Path()
        try:
            parser._parse_path_data(path, self.path_data)
        except ValueError as e:
            raise RuntimeError(f"Invalid SVG path data: {e}")
        context.set_current_path(path)
        context.render()

class SetColorCommand(GraphicsCommand):
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r, self.g, self.b, self.a = r, g, b, a

    def execute(self, context: 'GraphicsContext') -> None:
        context.set_color(self.r, self.g, self.b, self.a)

class SetFillRuleCommand(GraphicsCommand):
    def __init__(self, rule: str):
        self.rule = rule

    def execute(self, context: 'GraphicsContext') -> None:
        context.set_fill_rule(self.rule)

class SetLineWidthCommand(GraphicsCommand):
    def __init__(self, width: float):
        self.width = width

    def execute(self, context: 'GraphicsContext') -> None:
        context.set_line_width(self.width)

class SetLineCapCommand(GraphicsCommand):
    def __init__(self, cap: str):
        self.cap = cap

    def execute(self, context: 'GraphicsContext') -> None:
        context.set_line_cap(self.cap)

class SetLineJoinCommand(GraphicsCommand):
    def __init__(self, join: str):
        self.join = join

    def execute(self, context: 'GraphicsContext') -> None:
        context.set_line_join(self.join)

class SetLineDashCommand(GraphicsCommand):
    def __init__(self, pattern: List[float], offset: float = 0.0):
        self.pattern = pattern
        self.offset = offset

    def execute(self, context: 'GraphicsContext') -> None:
        context.set_line_dash(self.pattern, self.offset)

class GraphicsContext:
    _instance = None

    def __new__(cls, width: int = 400, height: int = 400):
        if cls._instance is None:
            cls._instance = super(GraphicsContext, cls).__new__(cls)
            cls._instance._initialize(width, height)
        return cls._instance

    def _initialize(self, width: int, height: int) -> None:
        stroke_props = None
        if StrokeProperties:
            stroke_props = StrokeProperties(
                width=1.0, color=(0, 0, 0, 255), line_cap=LineCap.BUTT, line_join=LineJoin.MITER
            )
        else:
            stroke_props = type('MockStroke', (), {
                'width': 1.0,
                'color': (0, 0, 0, 255),
                'line_cap': None,
                'line_join': None,
                'miter_limit': 4.0,
                'dash_pattern': None,
                'dash_offset': 0.0
            })()

        self.state = GraphicsState(
            rasterizer=AntiAliasedRasterizer(width, height) if AntiAliasedRasterizer else None,
            current_path=None,
            stroke_props=stroke_props,
            fill_props=None,
            canvas_width=width,
            canvas_height=height,
            transform=Transform.identity()
        )
        self.commands: Dict[str, Callable] = {}
        self._register_commands()

    def _register_commands(self) -> None:
        self.commands['draw-line'] = lambda x1, y1, x2, y2: DrawLineCommand(x1, y1, x2, y2).execute(self)
        self.commands['draw-circle'] = lambda cx, cy, r: DrawCircleCommand(cx, cy, r).execute(self)
        self.commands['draw-rectangle'] = lambda x, y, w, h: DrawRectangleCommand(x, y, w, h).execute(self)
        self.commands['draw-ellipse'] = lambda cx, cy, rx, ry: DrawEllipseCommand(cx, cy, rx, ry).execute(self)
        self.commands['draw-path'] = lambda data: DrawPathCommand(data).execute(self)
        self.commands['set-color'] = lambda r, g, b, a=255: SetColorCommand(r, g, b, a).execute(self)
        self.commands['set-fill-rule'] = lambda rule: SetFillRuleCommand(rule).execute(self)
        self.commands['set-line-width'] = lambda width: SetLineWidthCommand(width).execute(self)
        self.commands['set-line-cap'] = lambda cap: SetLineCapCommand(cap).execute(self)
        self.commands['set-line-join'] = lambda join: SetLineJoinCommand(join).execute(self)
        self.commands['set-line-dash'] = lambda pattern, offset=0.0: SetLineDashCommand(pattern, offset).execute(self)
        self.commands['clear-canvas'] = self.clear_canvas
        self.commands['set-canvas-size'] = self.set_canvas_size
        self.commands['save'] = self.save
        self.commands['translate'] = lambda dx, dy: self.apply_transform(Transform.translate(dx, dy))
        self.commands['rotate'] = lambda angle, cx=None, cy=None: self.apply_transform(
            Transform.rotate(angle, cx, cy))
        self.commands['scale'] = lambda sx, sy=None: self.apply_transform(Transform.scale(sx, sx if sy is None else sy))
        self.commands['reset-transform'] = self.reset_transform

    def set_current_path(self, path: Path) -> None:
        self.state.current_path = path

    def render(self) -> None:
        if not self.state.current_path or not self.state.rasterizer:
            return
        path = self.state.current_path.copy()
        path = path.transform(*self.state.transform)
        stroke = self.state.stroke_props
        if stroke:
            sx, _, _, sy, _, _ = self.state.transform
            scale = (abs(sx) + abs(sy)) / 2
            dash_pattern = stroke.dash_pattern
            dash_offset = stroke.dash_offset
            stroke = StrokeProperties(
                width=stroke.width * scale,
                color=stroke.color,
                line_cap=stroke.line_cap,
                line_join=stroke.line_join,
                miter_limit=stroke.miter_limit,
                dash_pattern=dash_pattern,
                dash_offset=dash_offset
            ) if StrokeProperties else stroke
        self.state.rasterizer.rasterize(
            path,
            self.state.canvas_width,
            self.state.canvas_height,
            stroke=stroke,
            fill=self.state.fill_props,
            existing_canvas=self.state.rasterizer.get_buffer()
        )
        self.state.current_path = None

    def set_color(self, r: int, g: int, b: int, a: int) -> None:
        color = (int(r), int(g), int(b), int(a))
        if StrokeProperties and isinstance(self.state.stroke_props, StrokeProperties):
            self.state.stroke_props = StrokeProperties(
                width=self.state.stroke_props.width,
                color=color,
                line_cap=self.state.stroke_props.line_cap,
                line_join=self.state.stroke_props.line_join,
                miter_limit=self.state.stroke_props.miter_limit,
                dash_pattern=self.state.stroke_props.dash_pattern,
                dash_offset=self.state.stroke_props.dash_offset
            )
        else:
            self.state.stroke_props.color = color
        self.state.fill_props = FillProperties(color=color, rule=EvenOddFillRule()) if FillProperties else None

    def set_fill_rule(self, rule: str) -> None:
        if not FillProperties:
            return
        rule = rule.lower()
        fill_rule = EvenOddFillRule() if rule == "evenodd" else NonZeroWindingFillRule()
        self.state.fill_props = FillProperties(
            color=self.state.fill_props.color if self.state.fill_props else (0, 0, 0, 255),
            rule=fill_rule
        )

    def set_line_width(self, width: float) -> None:
        if StrokeProperties and isinstance(self.state.stroke_props, StrokeProperties):
            self.state.stroke_props = StrokeProperties(
                width=float(width),
                color=self.state.stroke_props.color,
                line_cap=self.state.stroke_props.line_cap,
                line_join=self.state.stroke_props.line_join,
                miter_limit=self.state.stroke_props.miter_limit,
                dash_pattern=self.state.stroke_props.dash_pattern,
                dash_offset=self.state.stroke_props.dash_offset
            )
        else:
            self.state.stroke_props.width = float(width)

    def set_line_cap(self, cap: str) -> None:
        if not self.state.stroke_props:
            return
        cap = cap.lower()
        line_cap = {'butt': LineCap.BUTT, 'round': LineCap.ROUND, 'square': LineCap.SQUARE}.get(cap, LineCap.BUTT)
        if StrokeProperties and isinstance(self.state.stroke_props, StrokeProperties):
            self.state.stroke_props = StrokeProperties(
                width=self.state.stroke_props.width,
                color=self.state.stroke_props.color,
                line_cap=line_cap,
                line_join=self.state.stroke_props.line_join,
                miter_limit=self.state.stroke_props.miter_limit,
                dash_pattern=self.state.stroke_props.dash_pattern,
                dash_offset=self.state.stroke_props.dash_offset
            )
        else:
            self.state.stroke_props.line_cap = line_cap

    def set_line_join(self, join: str) -> None:
        if not self.state.stroke_props:
            return
        join = join.lower()
        line_join = {'miter': LineJoin.MITER, 'round': LineJoin.ROUND, 'bevel': LineJoin.BEVEL}.get(join, LineJoin.MITER)
        if StrokeProperties and isinstance(self.state.stroke_props, StrokeProperties):
            self.state.stroke_props = StrokeProperties(
                width=self.state.stroke_props.width,
                color=self.state.stroke_props.color,
                line_cap=self.state.stroke_props.line_cap,
                line_join=line_join,
                miter_limit=self.state.stroke_props.miter_limit,
                dash_pattern=self.state.stroke_props.dash_pattern,
                dash_offset=self.state.stroke_props.dash_offset
            )
        else:
            self.state.stroke_props.line_join = line_join

    def set_line_dash(self, pattern: List[float], offset: float) -> None:
        if not self.state.stroke_props:
            return
        if StrokeProperties and isinstance(self.state.stroke_props, StrokeProperties):
            self.state.stroke_props = StrokeProperties(
                width=self.state.stroke_props.width,
                color=self.state.stroke_props.color,
                line_cap=self.state.stroke_props.line_cap,
                line_join=self.state.stroke_props.line_join,
                miter_limit=self.state.stroke_props.miter_limit,
                dash_pattern=[float(p) for p in pattern],
                dash_offset=float(offset)
            )
        else:
            self.state.stroke_props.dash_pattern = [float(p) for p in pattern]
            self.state.stroke_props.dash_offset = float(offset)

    def clear_canvas(self) -> None:
        if self.state.rasterizer:
            self.state.rasterizer = AntiAliasedRasterizer(self.state.canvas_width, self.state.canvas_height)
        self.state.current_path = None

    def set_canvas_size(self, width: int, height: int) -> None:
        self.state.canvas_width = int(width)
        self.state.canvas_height = int(height)
        if AntiAliasedRasterizer:
            self.state.rasterizer = AntiAliasedRasterizer(int(width), int(height))
        self.state.current_path = None

    def save(self, filename: str) -> None:
        if self.state.rasterizer and save_to_png:
            canvas = self.state.rasterizer.get_buffer()
            save_to_png(canvas, filename, self.state.canvas_width, self.state.canvas_height)

    def apply_transform(self, matrix: List[float]) -> None:
        self.state.transform = Transform.multiply(self.state.transform, matrix)

    def reset_transform(self) -> None:
        self.state.transform = Transform.identity()

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.bindings: Dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any) -> Any:
        self.bindings[name] = value
        return value

    def get(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")

    def set(self, name: str, value: Any) -> Any:
        if name in self.bindings:
            self.bindings[name] = value
            return value
        if self.parent:
            return self.parent.set(name, value)
        raise RuntimeError(f"Cannot set undefined variable: {name}")

    def contains(self, name: str) -> bool:
        if name in self.bindings:
            return True
        return self.parent.contains(name) if self.parent else False

class Procedure:
    def __init__(self, params: List[str], body: Any, env: Environment, interpreter: 'Lisp'):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter

    def __call__(self, *args):
        if len(args) != len(self.params):
            raise RuntimeError(f"Expected {len(self.params)} arguments, got {len(args)}")
        env = Environment(self.env)
        for param, arg in zip(self.params, args):
            env.define(param, arg)
        return self.interpreter.eval(self.body, env)

    def __repr__(self):
        return f"<Procedure: ({', '.join(self.params)})>"

class Lisp:
    SPECIAL_FORMS = {
        'quote', 'if', 'define', 'lambda', 'begin', 'let', 'let*', 'letrec',
        'set!', 'while', 'cond', 'and', 'or', 'define-macro'
    }

    def __init__(self):
        self.global_env = Environment()
        self.graphics_context = GraphicsContext()
        self._setup_global_environment()

    def _setup_global_environment(self):
        self._setup_arithmetic()
        self._setup_logical()
        self._setup_list_operations()
        self._setup_string_operations()
        self._setup_control_flow()
        self._setup_graphics()

    def _setup_arithmetic(self):
        self.global_env.define('+', lambda *args: sum(float(arg) for arg in args))
        self.global_env.define('-', lambda a, *args: float(a) - sum(float(arg) for arg in args) if args else -float(a))
        self.global_env.define('*', lambda *args: 1 if not args else self._multiply_all(args))
        self.global_env.define('/', lambda a, *args: 1 / float(a) if not args else self._divide(a, args))
        self.global_env.define('%', lambda a, b: float(a) % float(b))
        self.global_env.define('expt', lambda a, b: float(a) ** float(b))
        self.global_env.define('abs', lambda x: abs(float(x)))
        self.global_env.define('min', lambda *args: min(float(arg) for arg in args))
        self.global_env.define('max', lambda *args: max(float(arg) for arg in args))
        self.global_env.define('floor', lambda x: int(float(x) // 1))
        self.global_env.define('ceiling', lambda x: int(float(x) // 1 + (1 if float(x) % 1 else 0)))
        self.global_env.define('round', lambda x: round(float(x)))

    def _setup_logical(self):
        self.global_env.define('true', True)
        self.global_env.define('false', False)
        self.global_env.define('=', lambda a, b: float(a) == float(b))
        self.global_env.define('<', lambda a, b: float(a) < float(b))
        self.global_env.define('>', lambda a, b: float(a) > float(b))
        self.global_env.define('<=', lambda a, b: float(a) <= float(b))
        self.global_env.define('>=', lambda a, b: float(a) >= float(b))
        self.global_env.define('!=', lambda a, b: float(a) != float(b))
        self.global_env.define('equal?', lambda a, b: a == b)
        self.global_env.define('not', lambda x: not x)

    def _setup_list_operations(self):
        self.global_env.define('cons', lambda a, b: [a] + b if isinstance(b, list) else [a, b])
        self.global_env.define('car', lambda x: x[0] if x else None)
        self.global_env.define('cdr', lambda x: x[1:] if x else [])
        self.global_env.define('list', lambda *args: list(args))
        self.global_env.define('append', lambda *args: sum([arg if isinstance(arg, list) else [arg] for arg in args], []))
        self.global_env.define('null?', lambda x: x == [] or x is None)
        self.global_env.define('empty?', lambda x: len(x) == 0 if isinstance(x, list) else False)
        self.global_env.define('length', lambda x: len(x) if isinstance(x, list) else 0)
        self.global_env.define('map', lambda f, lst: [f(x) for x in lst])
        self.global_env.define('filter', lambda f, lst: [x for x in lst if f(x)])
        self.global_env.define('reduce', self._reduce)

    def _setup_string_operations(self):
        def string_append(*args):
            def strip_quotes(s):
                if isinstance(s, str) and s.startswith('"') and s.endswith('"'):
                    return s[1:-1]
                return str(s)
            return '"' + ''.join(strip_quotes(arg) for arg in args) + '"'
        self.global_env.define('string-append', string_append)
        self.global_env.define('string-length', lambda s: len(s) - 2 if isinstance(s, str) and s.startswith('"') and s.endswith('"') else len(s))
        self.global_env.define('substring', lambda s, start, end=None: 
            '"' + (s[start+1:end+1] if end is not None else s[start+1:-1]) + '"' 
            if isinstance(s, str) and s.startswith('"') and s.endswith('"') else s[start:end])

    def _setup_control_flow(self):
        self.global_env.define('display', lambda *args: print(*args, end=""))
        self.global_env.define('newline', lambda: print())
        self.global_env.define('print', print)
        self.global_env.define('compose', lambda f, g: lambda *args: f(g(*args)))
        self.global_env.define('pipe', lambda x, *funcs: self._pipe(x, funcs))
        self.global_env.define('apply', lambda f, args: f(*args))
        self.global_env.define('number?', lambda x: isinstance(x, (int, float)))
        self.global_env.define('integer?', lambda x: isinstance(x, int) or (isinstance(x, float) and x.is_integer()))
        self.global_env.define('float?', lambda x: isinstance(x, float))
        self.global_env.define('symbol?', lambda x: isinstance(x, str) and not (x.startswith('"') and x.endswith('"')))
        self.global_env.define('string?', lambda x: isinstance(x, str) and x.startswith('"') and x.endswith('"'))
        self.global_env.define('list?', lambda x: isinstance(x, list))
        self.global_env.define('procedure?', lambda x: callable(x) or isinstance(x, Procedure))
        self.global_env.define('boolean?', lambda x: isinstance(x, bool))

    def _setup_graphics(self):
        self.global_env.define('point', lambda x, y: {'x': float(x), 'y': float(y)})
        for name, func in self.graphics_context.commands.items():
            self.global_env.define(name, func)
        self.global_env.define('draw-text', lambda p, text, size: self._draw_text(p, text, size))

    def _draw_text(self, p: Dict, text: str, size: float) -> None:
        if not isinstance(p, dict) or 'x' not in p or 'y' not in p:
            raise RuntimeError("draw-text: first argument must be a point")
        if not isinstance(text, str) or not (text.startswith('"') and text.endswith('"')):
            raise RuntimeError("draw-text: second argument must be a string")
        if not self.graphics_context.state.rasterizer or not self.graphics_context.state.stroke_props:
            return
        point = Point(p['x'], p['y']).transform(*self.graphics_context.state.transform) if Point else p
        text_content = text[1:-1]
        color = self.graphics_context.state.stroke_props.color
        sx, _, _, sy, _, _ = self.graphics_context.state.transform
        scale = (abs(sx) + abs(sy)) / 2
        scaled_size = size * scale
        if hasattr(self.graphics_context.state.rasterizer, 'draw_text'):
            self.graphics_context.state.rasterizer.draw_text(point, text_content, scaled_size, color)

    def _multiply_all(self, args):
        result = 1
        for arg in args:
            result *= float(arg)
        return result

    def _divide(self, a: float, args: List[float]) -> float:
        result = float(a)
        for arg in args:
            if float(arg) == 0:
                raise RuntimeError("Division by zero")
            result /= float(arg)
        return result

    def _reduce(self, f, lst, initial=None):
        if not lst and initial is None:
            raise RuntimeError("reduce: empty list with no initial value")
        result = initial if initial is not None else lst[0]
        start = 0 if initial is not None else 1
        for x in lst[start:]:
            result = f(result, x)
        return result

    def _pipe(self, x, funcs):
        result = x
        for f in funcs:
            result = f(result)
        return result

    def tokenize(self, program: str) -> List[str]:
        # Add spaces around parentheses and quotes
        program = program.replace('(', ' ( ').replace(')', ' ) ').replace("'", " ' ")
        # Use regex to split tokens, preserving quoted strings
        token_pattern = r'"[^"]*"|[^\s()]+|\(|\)|\''
        tokens = [t for t in re.findall(token_pattern, program) if t.strip()]
        # Convert ' to (quote ...)
        result = []
        i = 0
        while i < len(tokens):
            if tokens[i] == "'":
                result.append('(')
                result.append('quote')
                i += 1
                if i < len(tokens) and tokens[i] != '(':
                    result.append('(')
                    result.append(tokens[i])
                    result.append(')')
                continue
            result.append(tokens[i])
            i += 1
        return result

    def parse(self, program: str) -> List[Any]:
        tokens = self.tokenize(program)
        open_count = tokens.count('(')
        close_count = tokens.count(')')
        if open_count != close_count:
            raise SyntaxError(f"Unbalanced parentheses: {open_count} opening and {close_count} closing")
        parsed = self._read_from_tokens(tokens)
        if not parsed:
            raise SyntaxError("Empty program")
        if len(parsed) == 1:
            return parsed[0]
        return parsed

    def _read_from_tokens(self, tokens: List[str]) -> List[Any]:
        if not tokens:
            return []
        result = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '(':
                i += 1
                sublist = []
                open_parens = 1
                while i < len(tokens) and open_parens > 0:
                    if tokens[i] == '(':
                        open_parens += 1
                    elif tokens[i] == ')':
                        open_parens -= 1
                    if open_parens == 0:
                        break
                    sublist.append(tokens[i])
                    i += 1
                if open_parens > 0:
                    raise SyntaxError("Missing closing parenthesis")
                result.append(self._read_from_tokens(sublist))
                i += 1
            elif token == ')':
                raise SyntaxError("Unexpected closing parenthesis")
            else:
                result.append(self._atom(token))
                i += 1
        return result

    def _atom(self, token: str) -> Any:
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                if token == 'true':
                    return True
                if token == 'false':
                    return False
                if token.startswith('"') and token.endswith('"'):
                    return token
                return token

    def eval(self, expr: Any, env: Optional[Environment] = None) -> Any:
        if env is None:
            env = self.global_env
        if isinstance(expr, (int, float, bool)) or (isinstance(expr, str) and expr.startswith('"')):
            return expr
        if isinstance(expr, str):
            if not expr.strip():
                raise SyntaxError("Invalid empty symbol")
            return env.get(expr)
        if not isinstance(expr, list):
            raise SyntaxError(f"Invalid expression: {expr}")
        if not expr:
            raise SyntaxError("Empty expression")
        first, *rest = expr

        if isinstance(first, str) and first in self.SPECIAL_FORMS:
            if first == 'quote':
                if len(expr) != 2:
                    raise SyntaxError("quote requires exactly one argument")
                return rest[0]
            elif first == 'if':
                if len(expr) != 4:
                    raise SyntaxError("if requires exactly three arguments: test, then, else")
                test, then, else_ = rest
                return self.eval(then, env) if self.eval(test, env) else self.eval(else_, env)
            elif first == 'define':
                if len(expr) < 3:
                    raise SyntaxError("define requires at least two arguments")
                if isinstance(rest[0], list):
                    if not rest[0]:
                        raise SyntaxError("define: function name required")
                    name, params = rest[0][0], rest[0][1:]
                    if not all(isinstance(p, str) for p in params):
                        raise SyntaxError("define: parameters must be symbols")
                    body = rest[1]
                    return env.define(name, Procedure(params, body, env, self))
                else:
                    if not isinstance(rest[0], str):
                        raise SyntaxError("define: variable name must be a symbol")
                    name, value = rest[0], rest[1]
                    return env.define(name, self.eval(value, env))
            elif first == 'lambda':
                if len(expr) < 3:
                    raise SyntaxError("lambda requires at least two arguments")
                params = rest[0]
                if not isinstance(params, list) or not all(isinstance(p, str) for p in params):
                    raise SyntaxError("lambda: parameters must be a list of symbols")
                body = rest[1]
                return Procedure(params, body, env, self)
            elif first == 'begin':
                result = None
                for e in rest:
                    result = self.eval(e, env)
                return result
            elif first == 'let':
                if len(expr) < 3:
                    raise SyntaxError("let requires bindings and body")
                bindings, body = rest[0], rest[1:]
                if not isinstance(bindings, list) or not all(isinstance(b, list) and len(b) == 2 for b in bindings):
                    raise SyntaxError("let: invalid bindings")
                new_env = Environment(env)
                for var, val in bindings:
                    if not isinstance(var, str):
                        raise SyntaxError("let: variable names must be symbols")
                    new_env.define(var, self.eval(val, env))
                result = None
                for e in body:
                    result = self.eval(e, new_env)
                return result
            elif first == 'let*':
                if len(expr) < 3:
                    raise SyntaxError("let* requires bindings and body")
                bindings, body = rest[0], rest[1:]
                if not isinstance(bindings, list) or not all(isinstance(b, list) and len(b) == 2 for b in bindings):
                    raise SyntaxError("let*: invalid bindings")
                new_env = Environment(env)
                for var, val in bindings:
                    if not isinstance(var, str):
                        raise SyntaxError("let*: variable names must be symbols")
                    new_env.define(var, self.eval(val, new_env))
                result = None
                for e in body:
                    result = self.eval(e, new_env)
                return result
            elif first == 'letrec':
                if len(expr) < 3:
                    raise SyntaxError("letrec requires bindings and body")
                bindings, body = rest[0], rest[1:]
                if not isinstance(bindings, list) or not all(isinstance(b, list) and len(b) == 2 for b in bindings):
                    raise SyntaxError("letrec: invalid bindings")
                new_env = Environment(env)
                for var, _ in bindings:
                    if not isinstance(var, str):
                        raise SyntaxError("letrec: variable names must be symbols")
                    new_env.define(var, None)
                for var, val in bindings:
                    new_env.set(var, self.eval(val, new_env))
                result = None
                for e in body:
                    result = self.eval(e, new_env)
                return result
            elif first == 'set!':
                if len(expr) != 3:
                    raise SyntaxError("set! requires exactly two arguments")
                var, val = rest
                if not isinstance(var, str):
                    raise SyntaxError("set!: variable name must be a symbol")
                if not env.contains(var):
                    raise RuntimeError(f"set!: undefined variable {var}")
                return env.set(var, self.eval(val, env))
            elif first == 'while':
                if len(expr) < 3:
                    raise SyntaxError("while requires condition and body")
                condition, *body = rest
                result = None
                while self.eval(condition, env):
                    for e in body:
                        result = self.eval(e, env)
                return result
            elif first == 'cond':
                if len(expr) < 2:
                    raise SyntaxError("cond requires at least one clause")
                for clause in rest:
                    if not isinstance(clause, list) or len(clause) < 1:
                        raise SyntaxError("cond: invalid clause")
                    if clause[0] == 'else':
                        if len(clause) < 2:
                            raise SyntaxError("cond: else clause requires body")
                        result = None
                        for e in clause[1:]:
                            result = self.eval(e, env)
                        return result
                    if len(clause) < 2:
                        raise SyntaxError("cond: clause requires test and body")
                    test, *body = clause
                    if self.eval(test, env):
                        result = None
                        for e in body:
                            result = self.eval(e, env)
                        return result
                return None
            elif first == 'and':
                if len(expr) < 2:
                    return True
                result = True
                for e in rest:
                    result = self.eval(e, env)
                    if not result:
                        return False
                return result
            elif first == 'or':
                if len(expr) < 2:
                    return False
                for e in rest:
                    result = self.eval(e, env)
                    if result:
                        return result
                return False
            elif first == 'define-macro':
                if len(expr) < 3:
                    raise SyntaxError("define-macro requires name and body")
                name, *body = rest
                if not isinstance(name, str):
                    raise SyntaxError("define-macro: name must be a symbol")
                env.define(name, ('macro', body))
                return None
        else:
            proc = self.eval(first, env)
            args = [self.eval(arg, env) for arg in rest]
            if isinstance(proc, tuple) and proc[0] == 'macro':
                macro_body = proc[1]
                result = None
                for expr in macro_body:
                    result = self.eval(expr, env)
                return result
            if not callable(proc):
                raise RuntimeError(f"{first} is not a procedure")
            return proc(*args)

    def run(self, program: str) -> Any:
        parsed = self.parse(program)
        if isinstance(parsed, list) and len(parsed) > 1:
            result = None
            for expr in parsed:
                result = self.eval(expr, self.global_env)
            return result
        return self.eval(parsed, self.global_env)