# SVG 1.1 Renderer Architecture

## File Structure

```
svg_renderer/
├── __init__.py
├── renderer.py       # Main renderer class
├── elements/         # SVG element implementations
│   ├── __init__.py
│   ├── base.py       # Base element class
│   ├── shapes.py     # Basic shape elements (rect, circle, etc.)
│   ├── text.py       # Text-related elements
│   ├── paths.py      # Path elements and commands
│   ├── gradients.py  # Gradient definitions
│   └── filters.py    # Filter effects
├── parsers/          # SVG parsing functionality
│   ├── __init__.py
│   ├── xml_parser.py # XML parsing utilities
│   └── css_parser.py # CSS parsing for styling
├── styling/          # Style processing
│   ├── __init__.py
│   ├── css.py        # CSS implementation
│   └── colors.py     # Color handling
├── transforms/       # Transformation matrices
│   ├── __init__.py
│   └── matrix.py     # Transform implementations
└── utils/            # Utility functions
    ├── __init__.py
    ├── units.py      # Unit conversion
    └── viewbox.py    # ViewBox handling
```

## Core Components and API

### Main Renderer (`renderer.py`)

```python
class SVGRenderer:
    """
    Main SVG renderer class that handles the rendering pipeline.
    """
    
    def __init__(self, backend='cairo'):
        """
        Initialize the SVG renderer.
        
        Args:
            backend (str): Rendering backend ('cairo', 'pillow', etc.)
        """
        pass
        
    def load_from_file(self, filepath):
        """
        Load SVG from a file.
        
        Args:
            filepath (str): Path to the SVG file
            
        Returns:
            bool: Success or failure
        """
        pass
        
    def load_from_string(self, svg_string):
        """
        Load SVG from a string.
        
        Args:
            svg_string (str): SVG content as string
            
        Returns:
            bool: Success or failure
        """
        pass
        
    def render(self, output_path=None, width=None, height=None):
        """
        Render the SVG to the specified output.
        
        Args:
            output_path (str, optional): Path to save the rendered image
            width (int, optional): Output width in pixels
            height (int, optional): Output height in pixels
            
        Returns:
            Image: Rendered image object
        """
        pass
        
    def get_element_by_id(self, element_id):
        """
        Find an element by its ID.
        
        Args:
            element_id (str): ID of the element to find
            
        Returns:
            SVGElement: Found element or None
        """
        pass
```

### Base Element (`elements/base.py`)

```python
class SVGElement:
    """
    Base class for all SVG elements.
    """
    
    def __init__(self, element_id=None, attributes=None):
        """
        Initialize an SVG element.
        
        Args:
            element_id (str, optional): Element ID
            attributes (dict, optional): Element attributes
        """
        pass
        
    def render(self, context):
        """
        Render the element to the provided context.
        
        Args:
            context: Rendering context
        """
        pass
        
    def apply_transform(self, transform):
        """
        Apply a transformation to this element.
        
        Args:
            transform (Transform): Transform to apply
        """
        pass
        
    def get_bounds(self):
        """
        Get the bounding box of this element.
        
        Returns:
            tuple: (x, y, width, height)
        """
        pass
```

### Shape Elements (`elements/shapes.py`)

```python
class Rect(SVGElement):
    """Rectangle shape element."""
    
    def __init__(self, x=0, y=0, width=0, height=0, rx=None, ry=None, **kwargs):
        """
        Initialize a rectangle element.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            width (float): Width
            height (float): Height
            rx (float, optional): X corner radius
            ry (float, optional): Y corner radius
        """
        pass

class Circle(SVGElement):
    """Circle shape element."""
    
    def __init__(self, cx=0, cy=0, r=0, **kwargs):
        """
        Initialize a circle element.
        
        Args:
            cx (float): Center X coordinate
            cy (float): Center Y coordinate
            r (float): Radius
        """
        pass

class Ellipse(SVGElement):
    """Ellipse shape element."""
    
    def __init__(self, cx=0, cy=0, rx=0, ry=0, **kwargs):
        """
        Initialize an ellipse element.
        
        Args:
            cx (float): Center X coordinate
            cy (float): Center Y coordinate
            rx (float): X radius
            ry (float): Y radius
        """
        pass

class Line(SVGElement):
    """Line shape element."""
    
    def __init__(self, x1=0, y1=0, x2=0, y2=0, **kwargs):
        """
        Initialize a line element.
        
        Args:
            x1 (float): Start X coordinate
            y1 (float): Start Y coordinate
            x2 (float): End X coordinate
            y2 (float): End Y coordinate
        """
        pass

class Polyline(SVGElement):
    """Polyline shape element."""
    
    def __init__(self, points=None, **kwargs):
        """
        Initialize a polyline element.
        
        Args:
            points (list): List of points as (x,y) tuples
        """
        pass

class Polygon(SVGElement):
    """Polygon shape element."""
    
    def __init__(self, points=None, **kwargs):
        """
        Initialize a polygon element.
        
        Args:
            points (list): List of points as (x,y) tuples
        """
        pass
```

### Path Element (`elements/paths.py`)

```python
class Path(SVGElement):
    """SVG path element."""
    
    def __init__(self, d=None, **kwargs):
        """
        Initialize a path element.
        
        Args:
            d (str): Path data string
        """
        pass
        
    def parse_path_data(self, path_data):
        """
        Parse the path data string into commands.
        
        Args:
            path_data (str): SVG path data string
            
        Returns:
            list: List of path commands
        """
        pass

class PathCommand:
    """Base class for path commands."""
    
    def execute(self, context, current_point):
        """
        Execute this command on the rendering context.
        
        Args:
            context: Rendering context
            current_point: Current point (x, y)
            
        Returns:
            tuple: New current point
        """
        pass

# Implementations for M, L, C, Q, A, Z, etc. commands would follow
```

### Text Elements (`elements/text.py`)

```python
class Text(SVGElement):
    """SVG text element."""
    
    def __init__(self, x=0, y=0, text="", **kwargs):
        """
        Initialize a text element.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            text (str): Text content
        """
        pass

class Tspan(SVGElement):
    """SVG tspan element for nested text."""
    
    def __init__(self, x=None, y=None, dx=None, dy=None, text="", **kwargs):
        """
        Initialize a tspan element.
        
        Args:
            x (float, optional): Absolute X coordinate
            y (float, optional): Absolute Y coordinate
            dx (float, optional): Relative X offset
            dy (float, optional): Relative Y offset
            text (str): Text content
        """
        pass
```

### Gradient Elements (`elements/gradients.py`)

```python
class Gradient(SVGElement):
    """Base class for gradient elements."""
    
    def __init__(self, gradient_units='objectBoundingBox', gradient_transform=None, **kwargs):
        """
        Initialize a gradient.
        
        Args:
            gradient_units (str): 'userSpaceOnUse' or 'objectBoundingBox'
            gradient_transform (str, optional): Transformation to apply
        """
        pass
        
    def add_stop(self, offset, color, opacity=1.0):
        """
        Add a color stop to the gradient.
        
        Args:
            offset (float): Position from 0 to 1
            color (str): Color string
            opacity (float): Opacity from 0 to 1
        """
        pass

class LinearGradient(Gradient):
    """Linear gradient element."""
    
    def __init__(self, x1=0, y1=0, x2=1, y2=0, **kwargs):
        """
        Initialize a linear gradient.
        
        Args:
            x1 (float): Start X coordinate
            y1 (float): Start Y coordinate
            x2 (float): End X coordinate
            y2 (float): End Y coordinate
        """
        pass

class RadialGradient(Gradient):
    """Radial gradient element."""
    
    def __init__(self, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, **kwargs):
        """
        Initialize a radial gradient.
        
        Args:
            cx (float): Center X coordinate
            cy (float): Center Y coordinate
            r (float): Radius
            fx (float, optional): Focal point X coordinate
            fy (float, optional): Focal point Y coordinate
        """
        pass
```

### XML Parser (`parsers/xml_parser.py`)

```python
class SVGParser:
    """
    Parser for SVG XML content.
    """
    
    def __init__(self):
        """Initialize the SVG parser."""
        pass
        
    def parse(self, source):
        """
        Parse SVG content from file or string.
        
        Args:
            source (str): Filepath or XML string
            
        Returns:
            dict: Parsed SVG structure
        """
        pass
        
    def parse_element(self, element):
        """
        Parse an XML element into SVG element.
        
        Args:
            element: XML element
            
        Returns:
            SVGElement: Corresponding SVG element
        """
        pass
```

### Transform Handling (`transforms/matrix.py`)

```python
class Transform:
    """
    Handles SVG transformations with matrix operations.
    """
    
    def __init__(self, matrix=None):
        """
        Initialize a transformation.
        
        Args:
            matrix (list, optional): 3x3 transformation matrix
        """
        pass
        
    @classmethod
    def parse(cls, transform_str):
        """
        Parse an SVG transform string.
        
        Args:
            transform_str (str): SVG transform string
            
        Returns:
            Transform: Resulting transformation
        """
        pass
        
    def translate(self, tx, ty):
        """
        Add translation to this transform.
        
        Args:
            tx (float): X translation
            ty (float): Y translation
            
        Returns:
            Transform: Self for chaining
        """
        pass
        
    def scale(self, sx, sy=None):
        """
        Add scaling to this transform.
        
        Args:
            sx (float): X scaling factor
            sy (float, optional): Y scaling factor
            
        Returns:
            Transform: Self for chaining
        """
        pass
        
    def rotate(self, angle, cx=0, cy=0):
        """
        Add rotation to this transform.
        
        Args:
            angle (float): Rotation angle in degrees
            cx (float, optional): Center X coordinate
            cy (float, optional): Center Y coordinate
            
        Returns:
            Transform: Self for chaining
        """
        pass
        
    def skew_x(self, angle):
        """
        Add X-axis skew to this transform.
        
        Args:
            angle (float): Skew angle in degrees
            
        Returns:
            Transform: Self for chaining
        """
        pass
        
    def skew_y(self, angle):
        """
        Add Y-axis skew to this transform.
        
        Args:
            angle (float): Skew angle in degrees
            
        Returns:
            Transform: Self for chaining
        """
        pass
        
    def apply_to_point(self, x, y):
        """
        Apply transformation to a point.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            
        Returns:
            tuple: Transformed (x, y)
        """
        pass
```

### ViewBox Handling (`utils/viewbox.py`)

```python
class ViewBox:
    """
    Handles SVG viewBox attribute and coordinate transformations.
    """
    
    def __init__(self, min_x=0, min_y=0, width=None, height=None):
        """
        Initialize a viewBox.
        
        Args:
            min_x (float): Minimum X coordinate
            min_y (float): Minimum Y coordinate
            width (float): Width
            height (float): Height
        """
        pass
        
    @classmethod
    def parse(cls, viewbox_str):
        """
        Parse a viewBox string.
        
        Args:
            viewbox_str (str): viewBox attribute string
            
        Returns:
            ViewBox: Resulting viewBox
        """
        pass
        
    def get_transform(self, viewport_width, viewport_height, preserve_aspect_ratio="xMidYMid meet"):
        """
        Calculate transform from viewBox to viewport.
        
        Args:
            viewport_width (float): Target viewport width
            viewport_height (float): Target viewport height
            preserve_aspect_ratio (str): SVG preserveAspectRatio value
            
        Returns:
            Transform: Resulting transformation
        """
        pass
```

## Usage Example

Here's how you would use this SVG renderer API:

```python
from svg_renderer.renderer import SVGRenderer

# Create renderer
renderer = SVGRenderer(backend='cairo')

# Load SVG from file
renderer.load_from_file('my_drawing.svg')

# Or from string
svg_string = '''
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="80" height="80" fill="blue" />
</svg>
'''
renderer.load_from_string(svg_string)

# Render to file
renderer.render('output.png', width=200, height=200)

# Access and modify elements
rect = renderer.get_element_by_id('my-rect')
if rect:
    rect.attributes['fill'] = 'red'
    renderer.render('modified.png')
```

## Implementation Notes

1. **Backend Agnostic**: The architecture is designed to support multiple rendering backends (Cairo, Pillow, etc.) through an adapter pattern.

2. **Compliance**: This design covers the essential elements and attributes of SVG 1.1 specification.

3. **Extension Points**:
   - Add more element types in the elements/ directory
   - Implement additional filters in elements/filters.py
   - Support more CSS styling properties in styling/css.py

4. **Performance Considerations**:
   - Implement caching of parsed path data
   - Use transformation matrices for efficient transforms
   - Consider implementing a scene graph for complex SVGs

5. **Dependencies**:
   - For rendering: Cairo, Pillow, or similar graphics library
   - For XML parsing: Built-in xml.etree or lxml
