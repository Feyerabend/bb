
## PostScript


### 1. Project Overview and Initial Steps

The PostScript language is a stack-based, dynamically-typed language for
page description, so your project will need two primary components:

1. *Interpreter*: Parses and processes PostScript commands.
2. *Rasteriser*: Transforms vector descriptions and text into a pixel-based representation.

Before coding, familiarize yourself with the PostScript language's fundamentals,
particularly its graphics model, operators, and coordinate system.

* https://www.adobe.com/jp/print/postscript/pdfs/PLRM.pdf


Next, set up a minimal project structure that allows easy expansion.

### 2. Project Structure and File Organization

Here's a high-level view of how you could organize your project files:

```shell
ps_interpreter/
├── src/
│   ├── main.py                    # entry point for the project
│   ├── interpreter/
│   │   ├── ..
│   │   ├── lexer.py               # tokenizes PostScript commands
│   │   ├── parser.py              # parses tokens into executable statements
│   │   ├── executor.py            # executes parsed PostScript commands
│   │   ├── stack.py               # manages the operand stack
│   │   └── environment.py         # manages variable and function definitions
│   │
│   ├── rasteriser/
│   │   ├── ..
│   │   ├── renderer.py            # renders shapes and text to a buffer
│   │   ├── graphics_state.py      # tracks the graphics state (transformations, color, etc.)
│   │   ├── path.py                # manages paths and geometric data
│   │   └── output_buffer.py       # stores rasterised data for output
│   │
│   ├── utils/
│   │   ├── color_utils.py         # manages color conversions
│   │   ├── geometry_utils.py      # helper functions for geometric operations
│   │   └── transformations.py     # functions for translation, rotation, scaling
│
├── tests/                         # unit tests for each module
├── examples/                      # sample PostScript files to test the interpreter
└── README.md                      # project documentation
```


### 3. Detailed Steps and Module Breakdown


#### Step 1: Set Up the Interpreter

The interpreter reads PostScript commands, parses them, and manages the operand stack. This step will involve
modules for tokenizing commands, parsing them, and executing them within the correct context.

- Lexer (`lexer.py`): Tokenizes PostScript input into recognizable symbols like numbers, operators, and names.
  This module is essential to break down the input for parsing.

- Parser (`parser.py`): Organizes tokens into interpretable units, recognising PostScript language constructs
  such as loops, procedures, and control structures.

- Executor (`executor.py`): Executes parsed instructions by manipulating the operand stack and calling appropriate
  functions. Each PostScript operator (e.g. `moveto`, `lineto`, `stroke`) will have a corresponding function.

- Stack Management (`stack.py`): PostScript is stack-based, so the interpreter should use a stack to handle
  arguments and results.

- Environment (`environment.py`): Manages variables, procedures, and dictionaries, maintaining state across
  commands and supporting scoping rules.


#### Step 2: Set Up the Graphics State

The graphics state is a collection of parameters that affects how PostScript graphics operators work. This
includes things like the current transformation matrix, line width, and fill color.

- Graphics State (`graphics_state.py`): Tracks parameters such as color, transformations, and line style.
  It maintains the current transformation matrix (CTM) and other style attributes. PostScript commands
  modify this state and store it on a stack to support nested graphics contexts.


#### Step 3: Develop the Rasteriser

The rasteriser converts paths, shapes, and text commands into pixels, making use of the graphics state.
This component will likely involve modules to handle specific rendering tasks, such as filling paths and
rendering text.

- Renderer (`renderer.py`): Implements core rasterization logic, translating vector shapes into pixel
  data according to the graphics state. This module will handle operations like stroke, fill, and text rendering.

- Path Management (`path.py`): Represents and manipulates geometric paths, handling commands like `moveto`,
  `lineto`, `curveto`, and `closepath`. It supports constructing paths and converting them into rasterised form.

- Output Buffer (`output_buffer.py`): Stores the pixel data for the rendered image, which can be saved to a
  file or displayed. You might use a simple 2D array to represent pixel data and write it out as a PNG or other
  image format.


#### Step 4: Utility Modules

These will provide helper functions and classes to manage color, geometry, and transformations, aiding both
the interpreter and rasteriser.

- Color Utilities (color_utils.py): Handles color transformations (e.g., RGB to grayscale) and manages color
  mixing operations.

- Geometry Utilities (geometry_utils.py): Contains functions for geometric operations, like distance calculations
  and point transformations.

- Transformations (transformations.py): Implements translation, rotation, scaling, and matrix operations
  for the current transformation matrix.


#### Step 5: Testing and examples

To ensure each part works correctly, develop unit tests for individual components. For example, verify that the parser correctly
interprets commands and that the renderer produces accurate output for simple shapes. Create sample PostScript files to validate 
functionality as you progress.


### 4. Iterative Development Approach

1.	Basic Interpreter: Implement a minimal interpreter that can parse and execute simple arithmetic and
    stack operations, e.g. `3 4 add`.

2.	Basic Rasteriser: Implement basic rasterization for simple geometric shapes (e.g., lines, circles)
    and verify by displaying the results in the output buffer.

3.	Integration of Graphics State: Add graphics state handling, such as color and transformation. Extend
    the rasteriser to respect these attributes.

4.	Support for Paths and Complex Shapes: Enhance the interpreter and rasteriser to support complex paths
    and curves using commands like `moveto`, `lineto`, and `curveto`.

5.	Advanced Interpreter Features: Add support for control structures (e.g. `if`, `for`, and `repeat`) and
    procedures to allow more complex PostScript files to be interpreted.

6.	Text Rendering: Implement text support, managing the placement, rotation, and scaling of text in the 
    graphics state.

7.	Performance and Optimisation: Once the main functionality is complete, optimize for performance,
    especially in the rasteriser, where pixel-by-pixel manipulation can be costly.

Here's an outline of key functions for each module, focusing on their roles in a PostScript
interpreter and rasteriser. This outline is based on the suggested structure and splits
functionality to keep each module manageable.


#### 1. Interpreter Module

__`lexer.py`__

Handles breaking down the PostScript code into tokens.

- `tokenize(code: str) -> List[Token]`: Splits the input PostScript code into tokens,
  such as numbers, operators, names, and symbols.
- `is_number(token: str) -> bool`: Checks if a token represents a number.
- `is_operator(token: str) -> bool`: Checks if a token is a valid PostScript operator.


__`parser.py`__

Interprets tokens and organizes them into executable instructions.

- `parse(tokens: List[Token]) -> ASTNode`: Converts a list of tokens into an Abstract Syntax Tree (AST)
  or another structured format that's easier to interpret.
- `parse_expression(tokens: List[Token]) -> ASTNode`: Parses expressions, identifying and grouping tokens
  like if and for into executable expressions.


__`executor.py`__

Executes parsed commands, operating on the stack and interacting with other modules.

- `execute(ast: ASTNode)`: Interprets each AST node and executes commands by calling specific operator
  functions.
- `run_operator(operator: str, operands: List[Any]) -> Any`: Executes PostScript operators
  (e.g. `add`, `moveto`, `lineto`) using the operand stack.
- `evaluate_procedure(procedure: List[Token])`: Evaluates and executes user-defined procedures,
  typically stored in the environment.


__`stack.py`__

Implements the operand stack needed for PostScript operations.

- `push(value: Any)`: Pushes a value onto the stack.
- `pop() -> Any`: Pops the top value off the stack and returns it.
- `top() -> Any`: Returns the top value without removing it.

__`environment.py`__

Manages the environment, storing variables, functions, and nested scopes.

- `define(name: str, value: Any)`: Defines a variable or procedure with a given name.
- `lookup(name: str) -> Any`: Retrieves the value of a variable or procedure by name.
- `enter_scope()`: Pushes a new scope onto the environment stack.
- `exit_scope()`: Pops the current scope, restoring the previous one.


#### 2. Rasteriser Module

__`renderer.py`__

Handles the actual rasterization, converting shapes and text into pixels based on the graphics state.

- `render_path(path: Path, state: GraphicsState, buffer: OutputBuffer)`: Renders a vector path onto
  the output buffer according to the current graphics state (for stroke and fill operations).
- `render_text(text: str, position: Tuple[int, int], state: GraphicsState, buffer: OutputBuffer)`:
  Renders text at a given position based on the current graphics state.
- `apply_color(buffer: OutputBuffer, color: Tuple[int, int, int])`: Applies color settings to the buffer.


__`graphics_state.py`__

Manages the current graphics settings, such as transformations, colors, and line styles.

- `set_color(r: int, g: int, b: int)`: Sets the drawing color in the graphics state.
- `set_line_width(width: float)`: Sets the width for stroking paths.
- `set_transform(matrix: List[List[float]])`: Sets the transformation matrix in the graphics state.
- `push_state()`: Saves the current graphics state onto a stack.
- `pop_state()`: Restores the previous graphics state from the stack.


__`path.py`__

Defines and manages vector paths, handling PostScript drawing commands.

- `moveto(x: float, y: float)`: Starts a new subpath at the specified coordinates.
- `lineto(x: float, y: float)`: Adds a line to the current path from the current point to (x, y).
- `curveto(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float)`: Adds a cubic Bezier curve to the path.
- `closepath()`: Closes the current path, connecting the end back to the start.


__`output_buffer.py`__

Stores the pixel data for rasterised images, ready for display or saving to a file.

- `set_pixel(x: int, y: int, color: Tuple[int, int, int])`: Sets a pixel at (x, y) to the specified color.
- `clear()`: Clears the buffer, filling it with a default background color.
- `save(filename: str)`: Saves the buffer as an image file (e.g., PNG or BMP).


#### 3. Utility Module


`color_utils.py`

Provides helper functions for color operations.

- `rgb_to_gray(r: int, g: int, b: int) -> int`: Converts an RGB color to grayscale.
- `blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]`:
  Blends two colors according to a specified ratio.


`geometry_utils.py`

Contains helper functions for geometric calculations.

- `distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float`:
  Calculates the Euclidean distance between two points.
- `point_on_line(x0: float, y0: float, x1: float, y1: float, t: float) -> Tuple[float, float]`:
  Finds a point on a line segment from (x0, y0) to (x1, y1) based on parameter t (0 <= t <= 1).


`transformations.py`

Implements matrix transformations for scaling, rotating, and translating shapes.

- `translate(matrix: List[List[float]], dx: float, dy: float) -> List[List[float]]`: Applies a translation to the transformation matrix.
- `rotate(matrix: List[List[float]], angle: float) -> List[List[float]]`: Rotates the transformation matrix by a given angle.
- `scale(matrix: List[List[float]], sx: float, sy: float) -> List[List[float]]`: Scales the transformation matrix by (sx, sy).


##### 4. main.py (Entry Point)

- load_file(filename: str): Loads a PostScript file for processing.
- parse_and_execute(code: str): Tokenizes, parses, and executes the PostScript code.
- render_output(buffer: OutputBuffer): Displays or saves the final rendered image from the output buffer.

This function breakdown keeps each file focused on its responsibilities while ensuring that core tasks like parsing,
state management, and rendering are separated. It will allow you to work on components individually, making debugging
and testing simpler.

---


Defining classes will provide a solid structure for encapsulating functionality, making the codebase modular and easier
to manage. Here's a detailed breakdown of the classes, organized by module.

1. Interpreter Module

Token (`lexer.py`)

Represents individual tokens parsed from the input code.

Attributes:
- `type: str`: The type of the token (e.g. “operator”, “number”, “name”).
- `value: Any`: The actual value (e.g. the number itself or the operator symbol).
Methods:
- `__init__(self, type: str, value: Any)`: Initializes a token with its type and value.

Lexer (`lexer.py`)

Tokenizes raw PostScript code.

Methods:
- `__init__(self, code: str)`: Initializes the lexer with the input code.
- `tokenize(self) -> List[Token]`: Processes the input and returns a list of Token objects.

Parser (`parser.py`)

Converts tokens into structured representations (e.g. AST or expression trees).

Methods:
- `__init__(self, tokens: List[Token])`: Initializes the parser with a list of tokens.
- `parse(self) -> ASTNode`: Parses tokens into an abstract syntax tree (AST) or a similar structure.

ASTNode (`parser.py`)

Represents a node in the abstract syntax tree.

Attributes:
- `type: str`: Type of the node (e.g. “operator”, “expression”).
- `value: Any`: The value of the node (e.g. operator name or literal value).
- `children: List[ASTNode]`: Child nodes for expressions or nested statements.
Methods:
- `__init__(self, type: str, value: Any, children: Optional[List[ASTNode]] = None)`: Initializes an AST node.

Executor (`executor.py`)

Interprets the parsed code and executes it on the stack.

Methods:
- `__init__(self, stack: Stack, env: Environment)`: Initializes the executor with an operand stack and environment.
- `execute(self, ast: ASTNode)`: Interprets and executes a node.
- `evaluate_operator(self, operator: str, operands: List[Any])`: Executes an operator with given operands.

Stack (stack.py)

Manages the operand stack, where PostScript stores temporary values.

Attributes:
- `items: List[Any]`: A list that stores stack values.
Methods:
- `push(self, value: Any)`: Pushes a value onto the stack.
- `pop(self) -> Any`: Pops and returns the top value from the stack.
- `peek(self) -> Any`: Returns the top value without removing it.

Environment (`environment.py`)

Handles variable and procedure storage, maintaining nested scopes.

Attributes:
- `scope_stack: List[Dict[str, Any]]`: A stack of dictionaries, each representing a scope level.
Methods:
- `define(self, name: str, value: Any)`: Defines a variable or procedure in the current scope.
- `lookup(self, name: str) -> Any`: Retrieves a variable or procedure from the nearest scope.
- `enter_scope(self)`: Adds a new scope to the stack.
- `exit_scope(self)`: Removes the current scope, reverting to the previous one.

2. Rasteriser Module

GraphicsState (`graphics_state.py`)

Stores the current graphics settings, such as color, line width, and transformation matrix.

Attributes:
- `color: Tuple[int, int, int]`: Current drawing color.
- `line_width: float`: Width of lines for strokes.
- `transform_matrix: List[List[float]]`: Transformation matrix for scaling, translation, and rotation.
Methods:
- `__init__(self)`: Initializes with default graphics settings.
- `set_color(self, r: int, g: int, b: int)`: Sets the drawing color.
- `set_line_width(self, width: float)`: Updates the line width.
- `apply_transform(self, matrix: List[List[float]])`: Updates the transformation matrix.

Path (`path.py`)

Manages vector paths, including subpaths and path operations.

Attributes:
- points: List[Tuple[float, float]]: A list of points in the path.
- closed: bool: Indicates if the path is closed.
Methods:
- moveto(self, x: float, y: float): Starts a new subpath.
- lineto(self, x: float, y: float): Adds a line to the current subpath.
- curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float): Adds a Bezier curve.
- closepath(self): Closes the current path.

Renderer (`renderer.py`)

Renders paths, shapes, and text onto an output buffer.

Attributes:
- `buffer: OutputBuffer`: The buffer where rendered pixels are stored.
- `graphics_state`: GraphicsState: Current graphics state for rendering.
Methods:
- `render_path(self, path: Path)`: Renders a path based on the current graphics state.
- `render_text(self, text: str, position: Tuple[int, int])`: Renders text at a specified position.
- `apply_color(self)`: Sets the buffer's current color.

OutputBuffer (`output_buffer.py`)

Represents the pixel-based output, where rasterised images are stored.

Attributes:
- `width: int`: Width of the output buffer.
- `height: int`: Height of the output buffer.
- `pixels: List[List[Tuple[int, int, int]]]`: 2D array of pixels (RGB format).
Methods:
- __init__(self, width: int, height: int): Initializes the buffer with a specified size.
- set_pixel(self, x: int, y: int, color: Tuple[int, int, int]): Sets a pixel at (x, y) to a specific color.
- clear(self): Fills the buffer with a background color.
- save(self, filename: str): Saves the buffer to an image file.

3. Utility Module

ColorUtils (`color_utils.py`)

Provides color manipulation functions.

Static Methods:
- `rgb_to_gray(r: int, g: int, b: int) -> int`: Converts an RGB color to grayscale.
- `blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]`: Blends two colors by a specified ratio.

GeometryUtils (`geometry_utils.py`)

Provides helper functions for geometric operations.

Static Methods:
- `distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float`: Calculates distance between two points.
- `point_on_line(x0: float, y0: float, x1: float, y1: float, t: float) -> Tuple[float, float]`: Calculates a point on a line segment.

Transformations (`transformations.py`)

Handles transformations, such as translation, rotation, and scaling.

Static Methods:
- `translate(matrix: List[List[float]], dx: float, dy: float) -> List[List[float]]`: Applies translation to a transformation matrix.
- `rotate(matrix: List[List[float]], angle: float) -> List[List[float]]`: Rotates the transformation matrix.
- `scale(matrix: List[List[float]], sx: float, sy: float) -> List[List[float]]`: Scales the transformation matrix.

4. Main Script (`main.py`)

`InterpreterEngine`

Orchestrates the loading, parsing, execution, and rendering process.

Attributes
- `lexer`: Tokenizer for input code.
- `parser`: Parser for tokenized input.
- `executor`: Executor for running commands.
- `renderer`: Renderer for visual output.
Methods
- `__init__(self)`: Initialises the interpreter engine and its components.
- `load_file(self, filename: str)`: Loads a PostScript file for processing.
- `parse_and_execute(self)`: Tokenizes, parses, and executes code.
- `render_output(self)`: Displays or saves the rendered output.

This setup keeps each class focused on a specific responsibility, simplifying code management and testing.
Using this structure, you'll have a modular and scalable foundation for your interpreter and rasteriser.




### Structure

1. Interpreter Module

lexer.py

```python
class Token:
    def __init__(self, type: str, value: any):
        pass

class Lexer:
    def __init__(self, code: str):
        pass

    def tokenize(self) -> list[Token]:
        pass
```
parser.py

```python
class ASTNode:
    def __init__(self, type: str, value: any, children: list['ASTNode'] = None):
        pass

class Parser:
    def __init__(self, tokens: list[Token]):
        pass

    def parse(self) -> ASTNode:
        pass

    def parse_expression(self, tokens: list[Token]) -> ASTNode:
        pass
```

executor.py

```python
class Executor:
    def __init__(self, stack: 'Stack', env: 'Environment'):
        pass

    def execute(self, ast: ASTNode):
        pass

    def run_operator(self, operator: str, operands: list[any]) -> any:
        pass

    def evaluate_procedure(self, procedure: list[Token]):
        pass
```

stack.py

```python
class Stack:
    def __init__(self):
        pass

    def push(self, value: any):
        pass

    def pop(self) -> any:
        pass

    def peek(self) -> any:
        pass
```

environment.py

```python
class Environment:
    def __init__(self):
        pass

    def define(self, name: str, value: any):
        pass

    def lookup(self, name: str) -> any:
        pass

    def enter_scope(self):
        pass

    def exit_scope(self):
        pass
```

2. Rasteriser Module

graphics_state.py

```python
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
```

path.py

```python
class Path:
    def __init__(self):
        pass

    def moveto(self, x: float, y: float):
        pass

    def lineto(self, x: float, y: float):
        pass

    def curveto(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float):
        pass

    def closepath(self):
        pass
```

renderer.py

```python
class Renderer:
    def __init__(self, buffer: 'OutputBuffer', graphics_state: GraphicsState):
        pass

    def render_path(self, path: Path):
        pass

    def render_text(self, text: str, position: tuple[int, int]):
        pass

    def apply_color(self):
        pass
```

output_buffer.py

```python
class OutputBuffer:
    def __init__(self, width: int, height: int):
        pass

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        pass

    def clear(self):
        pass

    def save(self, filename: str):
        pass
```

3. Utility Module

color_utils.py

```python
class ColorUtils:
    @staticmethod
    def rgb_to_gray(r: int, g: int, b: int) -> int:
        pass

    @staticmethod
    def blend_colors(color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
        pass
```

geometry_utils.py

```python
class GeometryUtils:
    @staticmethod
    def distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
        pass

    @staticmethod
    def point_on_line(x0: float, y0: float, x1: float, y1: float, t: float) -> tuple[float, float]:
        pass
```

transformations.py

```python
class Transformations:
    @staticmethod
    def translate(matrix: list[list[float]], dx: float, dy: float) -> list[list[float]]:
        pass

    @staticmethod
    def rotate(matrix: list[list[float]], angle: float) -> list[list[float]]:
        pass

    @staticmethod
    def scale(matrix: list[list[float]], sx: float, sy: float) -> list[list[float]]:
        pass
```

4. Main Script

main.py

```python
class InterpreterEngine:
    def __init__(self):
        pass

    def load_file(self, filename: str):
        pass

    def parse_and_execute(self, code: str):
        pass

    def render_output(self):
        pass
```

This layout provides a modular, organized approach to implementing a PostScript interpreter and rasteriser.
Each class focuses on a distinct responsibility, making it easier to expand and debug as you implement the methods.
