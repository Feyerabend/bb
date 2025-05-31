
## Project: Develop Your Own 3D Engine in C

Many students in game development are drawn to learning C and C++ because these languages sit at the
heart of the game industry's technical foundation. A major reason is the sheer abundance of mature
libraries and engines--such as SDL, OpenGL, DirectX, Vulkan, Bullet Physics, and Unreal Engine--that
are either written in or provide first-class support for C and C++. This ecosystem gives learners
direct access to powerful, low-level tools for graphics, physics, input handling, audio, and networking.

Moreover, decades of accumulated knowledge about 3D rendering, real-time simulation, performance optimisation,
and memory management have been codified in the C/C++ programming culture. Many of the classic texts,
tutorials, and research papers in graphics and game development assume familiarity with these languages.
As a result, learning C/C++ gives students a gateway into this deep and well-documented tradition, which
can be invaluable for understanding how things really work under the hood—and for writing high-performance,
platform-level code where efficiency and control are critical.

In short, C and C++ offer not just tools but direct access to the accumulated technical wisdom of the
game development field.

Many also want to develop their own 3D engine for making games. Here the project can be structured as follows:

1. Set Up a Basic Rendering Pipeline
Begin with a minimal application using OpenGL or SDL to create a window and draw simple shapes. Learn how
to clear the screen, handle buffers, and draw colored triangles. This step introduces the fundamental flow
of a real-time rendering loop: *input → update → render*.

2. Implement a Math Library
To manipulate 3D geometry, you'll need basic linear algebra: vectors, matrices, dot and cross products,
transformations, and projections. Rather than relying on external libraries, implementing your own helps
solidify the mathematical concepts that underpin 3D engines.

3. Define and Load 3D Models
Add support for reading simple 3D model formats, such as OBJ. Learn to parse vertex positions, texture
coordinates, and normals. Display wireframes or flat-shaded models to validate your pipeline.

4. Build a Camera System
Introduce a movable camera with position, direction, and perspective projection. Implement user-controlled
movement (e.g. WASD + mouse look), which brings your 3D world to life and makes it navigable.

5. Add Lighting and Shading
Write basic GLSL shaders for diffuse and ambient lighting. Then add more complex effects like specular
highlights or point lights. Explore how normals and material properties affect visual realism.

6. Texture Mapping and Materials
Extend your renderer to support texture loading and mapping. Learn how to apply UV coordinates, sample
textures in shaders, and handle materials defined in OBJ/MTL files.

7. Scene Graph or Entity System
As complexity grows, you'll need a way to manage multiple objects and their transformations. Implement
a simple scene graph or entity-component system to organize updates, rendering, and object hierarchies.

8. Physics and Collision Detection
Incorporate a physics module or connect to a physics library like Bullet. Begin with bounding box or
sphere collision, then experiment with simple rigid body dynamics.

9. Optimisation and Performance Tools
Profile your engine and optimise hotspots. Introduce spatial partitioning structures (e.g., octrees or
BSP trees), frustum culling, or level-of-detail techniques to improve efficiency.

10.	Asset Pipeline and Scripting
Create a workflow for importing assets, defining scenes, and scripting behaviors. Consider embedding a
scripting language like Lua or writing a minimal configuration format.

11.	User Interface and Final Touches
Add a basic GUI system for debugging or menus. Final polish may include post-processing effects like
bloom, fog, or shadow mapping.


### Simple Start

If you're completely new to this field, a beginner-friendly starting point is provided in the folder [01](./01/).
This setup is designed to stay within the familiar territory of C, Python, and JavaScript, and we've intentionally
kept external dependencies to a minimum.

In this first part, we'll use:
- C for generating 3D geometry and rendering wireframes
- Python (with the Pillow library as an addition) for image processing
- JavaScript (in the browser) for viewing PAM files


__Step 1: Compile the Wireframe Renderer__

To generate a simple wireframe cube, compile the program with:

```shell
> make wireframe
```

This produces three output files:
- output.pam
- output2.pam
- points.pam

The first two files show the cube as a wireframe, rendered from different rotated positions.
The third file contains the 3D point data.

You can view the wireframe images using the provided pam7viewer.html tool in your browser.
The PAM7 format (in ASCII)[^pam] is simple to read and inspect manually, which makes it ideal for
learning and debugging.

[^pam]: See e.g. https://en.wikipedia.org/wiki/Netpbm#PAM_graphics_format.


__Step 2: Compile the Solid Renderer__

Next, compile the version that renders a solid-colored cube:

```shell
> make solid
```

This will generate a sequence of image files showing the cube rotating:
cube_frame_01.pam, cube_frame_02.pam, … up to cube_frame_15.pam.
Each frame shows the cube in a different orientation.


__Step 3: Merge Frames into an Animation__

Finally, you can merge the sequence of frames into a single animated image using:

```shell
> make merge
```

This creates an animated GIF, allowing you to easily view the rotating cube as a continuous animation.

This sequence of steps introduces the basics of 3D rendering, image processing, and minimal animation,
while keeping the system simple, transparent, and easily inspectable. You can walk this path for 
sometime, but eventually you will have to switch to other tools which makes much more sense developing
the engine further.


### Going Further

In [02](./02/), we delve into both general programming concepts and the specifics of rendering a rotating
cube. While we've primarily employed standard matrix operations thus far, alternative mathematical approaches
are available. These methods may present increased complexity in some aspects but offer simplifications in
others. The key takeaway is that solutions need not always follow traditional paths. By exploring and
experimenting with different techniques, you may uncover unexpected and valuable insights.

This is not in C, but prototyping in JavaScript to see how it affects the animation.


### Lighting

A model, like the cube in the code in [03](./03/), as you should be aware of now is made of vertices
connected to form faces (triangles here). The cube has 8 vertices and 12 triangular faces, each with
a color (red, green, blue, etc.).

- Model Space: Vertices start in a local coordinate system relative to the object's center.
- World Space: A transformation (translation for position, rotation for orientation) moves the model to a position
  in the 3D world. The cube is placed at (0.5, 0.5, 0.0) and rotates over time.
- View Space: The camera's position and orientation define a view. A view matrix shifts everything relative to the
  camera, as if you're looking from a specific spot (e.g., camera at (0.5, 1.5, 8.0)).
- Projection: A perspective projection matrix mimics human vision, making closer objects appear larger. It transforms
  3D coordinates into a "frustum" (a clipped 3D volume) based on field of view (45 degrees in the code), aspect ratio
  (800/600), and near/far planes (0.1 to 100). This maps 3D to a 2D-like space.

- Screen Space: The world_to_screen function converts projected coordinates to pixel positions on a 2D screen
  (800x600 pixels here), flipping the y-axis so higher y in world space appears lower on screen.
- Rasterisation: Triangles are drawn to a framebuffer (a memory buffer of pixels) by filling in the areas between
  vertices. Here we use a scanline method to color pixels inside each triangle.
- Output: The framebuffer's pixel data (RGB colors) is saved as images (PAM files), which can be viewed or
  combined into an animation.


#### Lighting in 3D Rendering

Lighting makes 3D scenes look more realistic by simulating how light interacts with surfaces. It affects colour
and brightness based on surface properties and light sources.

Light Types:
- Directional Light: A light source with a direction but no position (like the sun). The Light struct defines a
  direction, color, and intensity.
- Ambient Light: A constant, low-level light that brightens everything equally, preventing total darkness in shadows.
  The code has an ambient color and intensity (e.g., 0.3 intensity).


Lighting Model:
- Ambient Component: Multiplies the surface's base color (e.g., red face at 0.8, 0.2, 0.2) by the light's ambient
  color and intensity. This ensures the cube is visible even when not directly lit.
- Diffuse Component: Simulates light scattering based on the angle between the surface normal (a vector perpendicular
  to the face) and the light direction. The dot product in calculate_lighting computes this: if the normal faces the
  light, the surface is brighter. Here it clamps this to 0 or above (no negative light) and scales by light color and
  intensity (0.8).
- Final Color: Combines ambient and diffuse, clamped to 0-1, then scaled to 0-255 for RGB pixel values. Each face
  (red, green, blue, etc.) changes brightness as the light direction moves with time.

The create_default_light function sets a directional light (slightly warm white, moving direction), and calculate_lighting
applies it to each face's normal and base color, making the cube's appearance dynamic as it rotates.


#### Compile, Run and View

A Makefile automates compiling, running, and manages the project. It builds the renderer, runs it to create images of
the rotating, lit cube, and attempts to merge them.

```shell
make
```

Compiles: GCC turns main.c, model.c, rendering.c, and rmath.c into object files, then links them with the math library
(-lm) to create renderer.

Runs: Executes ./renderer, generating 60 PAM files (frame_000.pam to frame_059.pam), each showing the cube rotating with
lighting effects. Merges: Tries to run python3 pam7merge.py to combine PAM files into an animation (e.g., GIF).

You'll see output like “Rendering frame 1/60” and “Saved frame_000.pam”.

With pam7merge.py: If the script works, open animation.gif in a browser or image viewer to see the cube rotate, with
lighting shifting across its colored faces (red, green, blue, etc.). (The script requires installation of Pillow.)

Without Merging: Convert frames to PNG, then combine: convert frame_*.png -delay 10 -loop 0 animation.gif. Open
animation.gif to watch the lit, rotating cube.

The cube stays at a fixed position (0.5, 0.5, 0.0), rotating on x, y, and z axes, with light moving to highlight
different faces.


### Texture

Well testing further you might get better results on rendering textures .. [04](./04/). As the light also goes out?
