# Graphics VM Scripting Tutorial

This document provides a comprehensive guide to the scripting capabilities of the Graphics VM, a custom language interpreter for creating graphics. The VM processes scripts to generate images in the PPM format, supporting basic shapes, colors, and hierarchical grouping.

## Table of Contents
1. [Overview](#overview)
2. [Script Structure](#script-structure)
3. [Commands and Syntax](#commands-and-syntax)
   - [Canvas](#canvas)
   - [Circle](#circle)
   - [Rectangle](#rectangle)
   - [Triangle](#triangle)
   - [Group](#group)
   - [Render](#render)
4. [Color Specification](#color-specification)
5. [Example Scripts](#example-scripts)
6. [Running Scripts](#running-scripts)
7. [Limitations and Notes](#limitations-and-notes)

## Overview

The Graphics VM interprets a simple scripting language designed to define graphical scenes. Scripts are text files containing commands that specify the canvas size, shapes (circles, rectangles, triangles), colors, and grouping structures. The VM parses these scripts into an Abstract Syntax Tree (AST), executes the commands to build a scene graph, and renders the result into a PPM image file.

Key features:
- *Shapes*: Circle, Rectangle, Triangle
- *Colors*: Named colors or RGB values
- *Grouping*: Hierarchical composition of shapes
- *Output*: PPM image format
- *Memory Management*: Tracked allocations with leak detection

## Script Structure

A script is a text file with one command per line. Each command consists of a keyword followed by parameters, separated by spaces or tabs. Lines are processed sequentially, and the script must end with a `render` command to generate the output image.

- *Comments*: Lines starting with `#` or `//` are ignored.
- *Empty Lines*: Skipped during parsing.
- *Maximum Line Length*: 256 characters.
- *Maximum Script Size*: 10KB.

## Commands and Syntax

Below is a detailed description of each command, its syntax, and parameters.

### Canvas

Defines the dimensions of the output image.

*Syntax*:
```
canvas width height
```

*Parameters*:
- `width`: Integer, the width of the canvas in pixels (positive).
- `height`: Integer, the height of the canvas in pixels (positive).

*Notes*:
- Must appear at the start of the script if used.
- If omitted, defaults to 400x400 pixels (defined by `DEFAULT_WIDTH` and `DEFAULT_HEIGHT`).
- Currently, resizing after initialization is not supported; the VM uses initial dimensions.

*Example*:
```
canvas 800 600
```

### Circle

Creates a circle shape.

*Syntax*:
```
circle name centerX centerY radius color
```

*Parameters*:
- `name`: String, unique identifier for the circle.
- `centerX`: Integer, x-coordinate of the circle's center.
- `centerY`: Integer, y-coordinate of the circle's center.
- `radius`: Integer, radius of the circle (positive).
- `color`: Color specification (see [Color Specification](#color-specification)).

*Example*:
```
circle myCircle 200 200 50 red
```

### Rectangle

Creates a rectangle shape.

*Syntax*:
```
rectangle name x y width height color
```
or
```
rect name x y width height color
```

*Parameters*:
- `name`: String, unique identifier for the rectangle.
- `x`: Integer, x-coordinate of the top-left corner.
- `y`: Integer, y-coordinate of the top-left corner.
- `width`: Integer, width of the rectangle (positive).
- `height`: Integer, height of the rectangle (positive).
- `color`: Color specification.

*Example*:
```
rect myRect 100 100 200 150 blue
```

### Triangle

Creates a triangle shape.

*Syntax*:
```
triangle name x1 y1 x2 y2 x3 y3 color
```

*Parameters*:
- `name`: String, unique identifier for the triangle.
- `x1, y1`: Integers, coordinates of the first vertex.
- `x2, y2`: Integers, coordinates of the second vertex.
- `x3, y3`: Integers, coordinates of the third vertex.
- `color`: Color specification.

*Example*:
```
triangle myTriangle 150 300 250 300 200 200 yellow
```

### Group

Groups multiple shapes together for hierarchical rendering.

*Syntax*:
```
group name
[shape commands]
end
```

*Parameters*:
- `name`: String, unique identifier for the group.
- `end`: Marks the end of the group.

*Notes*:
- Shapes defined within a group are children of that group.
- Groups can be nested.
- A group is rendered by rendering all its children in order.
- Unmatched `end` commands trigger a warning but do not halt execution.

*Example*:
```
group myGroup
circle circle1 200 200 30 green
rect rect1 150 150 100 100 cyan
end
```

### Render

Triggers the rendering of all top-level components and their children.

*Syntax*:
```
render
```

*Parameters*: None.

*Notes*:
- Typically the last command in the script.
- Only root components (not part of any group) are rendered directly; groups handle their children.
- Outputs the image to the specified file.

*Example*:
```
render
```

## Color Specification

Colors can be specified in two ways:

1. *Named Colors*:
   - `red`: (255, 0, 0)
   - `green`: (0, 255, 0)
   - `blue`: (0, 0, 255)
   - `yellow`: (255, 255, 0)
   - `cyan`: (0, 255, 255)
   - `magenta`: (255, 0, 255)
   - `white`: (255, 255, 255)
   - `black`: (0, 0, 0)

2. *RGB Values*:
   - Format: `r,g,b`
   - Each value is an integer between 0 and 255.
   - Values are clamped to this range if outside.

*Examples*:
```
circle myCircle 200 200 50 red
rect myRect 100 100 200 150 0,128,255
```

## Example Scripts

### Simple Scene
Creates a canvas with a red circle and a blue rectangle.

```
canvas 400 400
circle circle1 200 200 50 red
rect rect1 150 100 100 200 blue
render
```

### Nested Groups
Demonstrates grouping with nested shapes.

```
canvas 600 600
group outerGroup
  circle circle1 300 300 100 yellow
  group innerGroup
    rect rect1 250 250 100 100 cyan
    triangle tri1 200 400 300 400 250 300 magenta
  end
end
render
```

### Complex Scene
Combines multiple shapes and colors.

```
canvas 800 600
group background
  rect bgRect 0 0 800 600 white
end
group shapes
  circle sun 700 100 50 yellow
  rect ground 0 400 800 200 green
  triangle tree 400 400 450 300 350 300 0,100,0
end
render
```

## Running Scripts

To run a script, compile the provided C code and execute the resulting program with the following command:

```
./program <script_file> [width] [height] [output_file]
```

*Arguments*:
- `script_file`: Path to the script file (required).
- `width`: Canvas width (optional, default: 400).
- `height`: Canvas height (optional, default: 400).
- `output_file`: Output PPM file (optional, default: `output.ppm`).

*Example*:
```
./graphics_vm myscript.txt 800 600 image.ppm
```

The program:
1. Reads the script file.
2. Initializes the VM with the specified or default dimensions.
3. Parses the script into an AST.
4. Executes the AST to build and render the scene.
5. Outputs the image as a PPM file.
6. Prints memory statistics for debugging.

## Limitations and Notes

- *Canvas Resizing*: The VM does not support resizing the canvas after initialization. The `canvas` command's dimensions are noted but not applied if different from the initial size.
- *Error Handling*: Errors (e.g., invalid parameters, memory allocation failures) cause the program to fail with an error message.
- *Shape Overlap*: Later shapes overwrite earlier ones in the image buffer (last rendered wins).
- *Coordinate System*: Origin (0,0) is the top-left corner, with x increasing to the right and y increasing downward.
- *Performance*: The rendering algorithm is pixel-based and not optimized for large images or complex scenes.
- *Memory Management*: The VM tracks allocations and reports leaks via `printMemoryStats()`. Ensure all components are freed correctly.
- *File Size Limit*: Scripts are capped at 10KB to prevent excessive memory use.
- *PPM Output*: The output is in ASCII PPM (P3) format, which is simple but results in large files for high-resolution images.

This tutorial covers the core scripting capabilities of the Graphics VM. For advanced usage, consider extending the language with additional shapes, transformations, or rendering optimizations.